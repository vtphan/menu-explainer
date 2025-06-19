from fastapi import FastAPI, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from enum import Enum
from database import get_db, Restaurant, Section, MenuItem
from pydantic import BaseModel


app = FastAPI(
    title="Menu Explainer API",
    description="API to browse restaurant menus with SQLite backend",
    version="2.0.0"
)


class SortBy(str, Enum):
    name = "name"
    price = "price"


class Order(str, Enum):
    asc = "asc"
    desc = "desc"


class MenuItemResponse(BaseModel):
    name: str
    description: Optional[str]
    price: Optional[float]
    section: str
    restaurant: str
    
    class Config:
        from_attributes = True


class RestaurantResponse(BaseModel):
    name: str
    
    class Config:
        from_attributes = True


class SectionResponse(BaseModel):
    name: str
    
    class Config:
        from_attributes = True


@app.get("/restaurants", tags=["Restaurants"], response_model=List[str])
def get_restaurants(db: Session = Depends(get_db)):
    """Return a list of all restaurant names."""
    restaurants = db.query(Restaurant).all()
    return [r.name for r in restaurants]


@app.get("/restaurants/{restaurant_name}", tags=["Menus"])
def get_restaurant_menu(restaurant_name: str, db: Session = Depends(get_db)):
    """Return the full menu for a specific restaurant."""
    restaurant = db.query(Restaurant).filter(Restaurant.name == restaurant_name).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_name}' not found")
    
    menu = {}
    for section in restaurant.sections:
        menu[section.name] = [
            {
                "name": item.name,
                "description": item.description,
                "price": item.price
            }
            for item in section.items
        ]
    
    return menu


@app.get("/restaurants/{restaurant_name}/sections", tags=["Menus"], response_model=List[str])
def get_restaurant_sections(restaurant_name: str, db: Session = Depends(get_db)):
    """Return a list of all section names for a specific restaurant."""
    restaurant = db.query(Restaurant).filter(Restaurant.name == restaurant_name).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_name}' not found")
    
    return [section.name for section in restaurant.sections]


@app.get("/restaurants/{restaurant_name}/sections/{section_name}", tags=["Menus"])
def get_section_items(restaurant_name: str, section_name: str, db: Session = Depends(get_db)):
    """Return all items in a specific section of a restaurant."""
    restaurant = db.query(Restaurant).filter(Restaurant.name == restaurant_name).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_name}' not found")
    
    section = db.query(Section).filter(
        Section.restaurant_id == restaurant.id,
        Section.name == section_name
    ).first()
    
    if not section:
        raise HTTPException(status_code=404, detail=f"Section '{section_name}' not found in restaurant '{restaurant_name}'")
    
    return [
        {
            "name": item.name,
            "description": item.description,
            "price": item.price
        }
        for item in section.items
    ]


@app.get("/restaurants/{restaurant_name}/items", tags=["Search"])
def get_restaurant_items(
    restaurant_name: str,
    price_gt: Optional[float] = Query(None, description="Filter items with price greater than"),
    price_lt: Optional[float] = Query(None, description="Filter items with price less than"),
    sort_by: Optional[SortBy] = Query(None, description="Sort items by name or price"),
    order: Order = Query(Order.asc, description="Sort order"),
    db: Session = Depends(get_db)
):
    """Return all items from a restaurant with optional filtering and sorting."""
    restaurant = db.query(Restaurant).filter(Restaurant.name == restaurant_name).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_name}' not found")
    
    # Query all items for this restaurant
    query = db.query(MenuItem).join(Section).filter(Section.restaurant_id == restaurant.id)
    
    # Apply price filters
    if price_gt is not None:
        query = query.filter(MenuItem.price > price_gt)
    if price_lt is not None:
        query = query.filter(MenuItem.price < price_lt)
    
    # Get items
    items = query.all()
    
    # Format response with section info
    result = [
        {
            "name": item.name,
            "description": item.description,
            "price": item.price,
            "section": item.section.name
        }
        for item in items
    ]
    
    # Apply sorting
    if sort_by:
        if sort_by == SortBy.name:
            result.sort(key=lambda x: x["name"], reverse=(order == Order.desc))
        elif sort_by == SortBy.price:
            # Sort items with prices first, then items without prices
            items_with_price = [item for item in result if item["price"] is not None]
            items_without_price = [item for item in result if item["price"] is None]
            
            items_with_price.sort(key=lambda x: x["price"], reverse=(order == Order.desc))
            result = items_with_price + items_without_price
    
    return result


# Cross-restaurant search endpoints
@app.get("/search/items", tags=["Cross-Restaurant Search"], response_model=List[MenuItemResponse])
def search_items(
    query: Optional[str] = Query(None, description="Search in item names and descriptions"),
    price_gt: Optional[float] = Query(None, description="Filter items with price greater than"),
    price_lt: Optional[float] = Query(None, description="Filter items with price less than"),
    restaurant: Optional[str] = Query(None, description="Filter by restaurant name"),
    sort_by: Optional[SortBy] = Query(None, description="Sort items by name or price"),
    order: Order = Query(Order.asc, description="Sort order"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Search for menu items across all restaurants."""
    # Base query
    query_obj = db.query(MenuItem).join(Section).join(Restaurant)
    
    # Apply search filter
    if query:
        search_pattern = f"%{query}%"
        query_obj = query_obj.filter(
            (MenuItem.name.ilike(search_pattern)) | 
            (MenuItem.description.ilike(search_pattern))
        )
    
    # Apply price filters
    if price_gt is not None:
        query_obj = query_obj.filter(MenuItem.price > price_gt)
    if price_lt is not None:
        query_obj = query_obj.filter(MenuItem.price < price_lt)
    
    # Apply restaurant filter
    if restaurant:
        query_obj = query_obj.filter(Restaurant.name == restaurant)
    
    # Apply sorting
    if sort_by == SortBy.name:
        query_obj = query_obj.order_by(
            MenuItem.name.desc() if order == Order.desc else MenuItem.name
        )
    elif sort_by == SortBy.price:
        # Sort NULL prices last
        if order == Order.desc:
            query_obj = query_obj.order_by(MenuItem.price.desc().nullslast())
        else:
            query_obj = query_obj.order_by(MenuItem.price.asc().nullslast())
    
    # Execute query with limit
    items = query_obj.limit(limit).all()
    
    # Format response
    return [
        MenuItemResponse(
            name=item.name,
            description=item.description,
            price=item.price,
            section=item.section.name,
            restaurant=item.section.restaurant.name
        )
        for item in items
    ]


@app.get("/search/by-price-range", tags=["Cross-Restaurant Search"], response_model=List[MenuItemResponse])
def search_by_price_range(
    min_price: float = Query(..., ge=0, description="Minimum price"),
    max_price: float = Query(..., ge=0, description="Maximum price"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Find all items within a specific price range across all restaurants."""
    if min_price > max_price:
        raise HTTPException(status_code=400, detail="min_price must be less than or equal to max_price")
    
    items = db.query(MenuItem).join(Section).join(Restaurant).filter(
        MenuItem.price >= min_price,
        MenuItem.price <= max_price
    ).order_by(MenuItem.price).limit(limit).all()
    
    return [
        MenuItemResponse(
            name=item.name,
            description=item.description,
            price=item.price,
            section=item.section.name,
            restaurant=item.section.restaurant.name
        )
        for item in items
    ]


@app.get("/search/restaurants-with-item", tags=["Cross-Restaurant Search"], response_model=List[str])
def find_restaurants_with_item(
    item_name: str = Query(..., description="Item name to search for (case-insensitive)"),
    db: Session = Depends(get_db)
):
    """Find all restaurants that have an item with the given name."""
    restaurants = db.query(Restaurant).join(Section).join(MenuItem).filter(
        MenuItem.name.ilike(f"%{item_name}%")
    ).distinct().all()
    
    return [r.name for r in restaurants]


@app.get("/stats/restaurant/{restaurant_name}", tags=["Statistics"])
def get_restaurant_stats(restaurant_name: str, db: Session = Depends(get_db)):
    """Get statistics about a restaurant's menu."""
    restaurant = db.query(Restaurant).filter(Restaurant.name == restaurant_name).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_name}' not found")
    
    total_items = 0
    items_with_price = 0
    total_price = 0
    min_price = None
    max_price = None
    
    for section in restaurant.sections:
        for item in section.items:
            total_items += 1
            if item.price is not None:
                items_with_price += 1
                total_price += item.price
                if min_price is None or item.price < min_price:
                    min_price = item.price
                if max_price is None or item.price > max_price:
                    max_price = item.price
    
    return {
        "restaurant": restaurant_name,
        "total_sections": len(restaurant.sections),
        "total_items": total_items,
        "items_with_price": items_with_price,
        "items_without_price": total_items - items_with_price,
        "average_price": round(total_price / items_with_price, 2) if items_with_price > 0 else None,
        "min_price": min_price,
        "max_price": max_price
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)