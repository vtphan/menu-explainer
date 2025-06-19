from typing import List, Dict, Any, Optional
from enum import Enum


class SortBy(str, Enum):
    name = "name"
    price = "price"


class Order(str, Enum):
    asc = "asc"
    desc = "desc"


def sort_menu_items(
    items: List[Dict[str, Any]], 
    sort_by: Optional[SortBy] = None, 
    order: Order = Order.asc
) -> List[Dict[str, Any]]:
    """Sort menu items by name or price."""
    if not sort_by:
        return items
    
    if sort_by == SortBy.name:
        return sorted(
            items, 
            key=lambda x: x.get("name", "").lower(), 
            reverse=(order == Order.desc)
        )
    elif sort_by == SortBy.price:
        # Separate items with and without prices
        items_with_price = [item for item in items if item.get("price") is not None]
        items_without_price = [item for item in items if item.get("price") is None]
        
        # Sort items with prices
        items_with_price.sort(
            key=lambda x: x["price"], 
            reverse=(order == Order.desc)
        )
        
        # Return items with prices first, then items without prices
        return items_with_price + items_without_price
    
    return items