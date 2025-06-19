from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional, Dict, Any
import json
from enum import Enum

# Initialize FastAPI app
app = FastAPI(
    title="Restaurant Menu API",
    description="API for serving restaurant menu data",
    version="1.0.0"
)

# Load menu data
with open("menus.json", "r") as f:
    menu_data = json.load(f)


class SortBy(str, Enum):
    name = "name"
    price = "price"


class Order(str, Enum):
    asc = "asc"
    desc = "desc"


@app.get("/restaurants", tags=["Restaurants"])
def list_restaurants() -> List[str]:
    """List all restaurant names."""
    return list(menu_data.keys())


@app.get("/restaurants/{restaurant_name}", tags=["Menus"])
def get_restaurant_menu(restaurant_name: str) -> Dict[str, Any]:
    """Return the full menu for the given restaurant."""
    if restaurant_name not in menu_data:
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_name}' not found")
    return menu_data[restaurant_name]


@app.get("/restaurants/{restaurant_name}/sections", tags=["Menus"])
def list_restaurant_sections(restaurant_name: str) -> List[str]:
    """List all section names for a restaurant."""
    if restaurant_name not in menu_data:
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_name}' not found")
    
    sections = menu_data[restaurant_name].get("sections", [])
    return [section["name"] for section in sections]


@app.get("/restaurants/{restaurant_name}/sections/{section_name}", tags=["Menus"])
def get_section_items(restaurant_name: str, section_name: str) -> List[Dict[str, Any]]:
    """Return all items in a section."""
    if restaurant_name not in menu_data:
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_name}' not found")
    
    sections = menu_data[restaurant_name].get("sections", [])
    
    # Find the section
    for section in sections:
        if section["name"] == section_name:
            return section.get("items", [])
    
    raise HTTPException(status_code=404, detail=f"Section '{section_name}' not found in restaurant '{restaurant_name}'")


@app.get("/restaurants/{restaurant_name}/items", tags=["Search"])
def get_all_items(
    restaurant_name: str,
    price_gt: Optional[float] = Query(None, description="Filter items with price > X"),
    price_lt: Optional[float] = Query(None, description="Filter items with price < X"),
    sort_by: Optional[SortBy] = Query(None, description="Sort by name or price"),
    order: Optional[Order] = Query(Order.asc, description="Sort order: asc or desc")
) -> List[Dict[str, Any]]:
    """Return all menu items across all sections with optional filtering and sorting."""
    if restaurant_name not in menu_data:
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_name}' not found")
    
    # Collect all items from all sections
    all_items = []
    sections = menu_data[restaurant_name].get("sections", [])
    
    for section in sections:
        items = section.get("items", [])
        # Add section name to each item for context
        for item in items:
            item_copy = item.copy()
            item_copy["section"] = section["name"]
            all_items.append(item_copy)
    
    # Filter by price if specified
    if price_gt is not None:
        all_items = [item for item in all_items if item.get("price", 0) > price_gt]
    
    if price_lt is not None:
        all_items = [item for item in all_items if item.get("price", float('inf')) < price_lt]
    
    # Sort if specified
    if sort_by:
        reverse = (order == Order.desc)
        
        if sort_by == SortBy.name:
            all_items.sort(key=lambda x: x.get("name", ""), reverse=reverse)
        elif sort_by == SortBy.price:
            # For price sorting, handle items without price
            # Items without price are treated as 0 for sorting purposes
            all_items.sort(key=lambda x: x.get("price", 0), reverse=reverse)
    
    return all_items