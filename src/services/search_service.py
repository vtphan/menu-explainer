from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from src.repositories.restaurant_repository import RestaurantRepository
from src.core.exceptions import ValidationError
from src.utils.sorting import SortBy, Order


class SearchService:
    """Service layer for cross-restaurant search functionality."""
    
    def __init__(self, db: Session):
        self.repository = RestaurantRepository(db)
    
    def search_items(
        self,
        query: Optional[str] = None,
        price_gt: Optional[float] = None,
        price_lt: Optional[float] = None,
        restaurant: Optional[str] = None,
        sort_by: Optional[SortBy] = None,
        order: Order = Order.asc,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search for menu items across all restaurants."""
        # Get items from repository
        items = self.repository.search_items_across_restaurants(
            query_text=query,
            price_gt=price_gt,
            price_lt=price_lt,
            restaurant_name=restaurant,
            limit=limit
        )
        
        # Format response
        result = [
            {
                "name": item.name,
                "description": item.description,
                "price": item.price,
                "section": item.section.name,
                "restaurant": item.section.restaurant.name
            }
            for item in items
        ]
        
        # Apply sorting if requested
        if sort_by:
            if sort_by == SortBy.name:
                result.sort(key=lambda x: x["name"].lower(), reverse=(order == Order.desc))
            elif sort_by == SortBy.price:
                # Sort with prices first, then without prices
                items_with_price = [item for item in result if item["price"] is not None]
                items_without_price = [item for item in result if item["price"] is None]
                
                items_with_price.sort(key=lambda x: x["price"], reverse=(order == Order.desc))
                result = items_with_price + items_without_price
        
        return result
    
    def search_by_price_range(
        self, 
        min_price: float, 
        max_price: float, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Find all items within a specific price range across all restaurants."""
        if min_price > max_price:
            raise ValidationError("min_price must be less than or equal to max_price")
        
        items = self.repository.get_items_by_price_range(min_price, max_price, limit)
        
        return [
            {
                "name": item.name,
                "description": item.description,
                "price": item.price,
                "section": item.section.name,
                "restaurant": item.section.restaurant.name
            }
            for item in items
        ]
    
    def find_restaurants_with_item(self, item_name: str) -> List[str]:
        """Find all restaurants that have an item with the given name."""
        restaurants = self.repository.get_restaurants_with_item(item_name)
        return [r.name for r in restaurants]