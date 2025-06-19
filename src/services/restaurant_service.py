from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from src.repositories.restaurant_repository import RestaurantRepository
from src.core.exceptions import NotFoundError
from src.utils.sorting import sort_menu_items, SortBy, Order


class RestaurantService:
    """Service layer for restaurant business logic."""
    
    def __init__(self, db: Session):
        self.repository = RestaurantRepository(db)
    
    def get_all_restaurants(self) -> List[str]:
        """Get list of all restaurant names."""
        restaurants = self.repository.get_all()
        return [r.name for r in restaurants]
    
    def get_restaurant_menu(self, restaurant_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get full menu for a restaurant."""
        restaurant = self.repository.get_by_name(restaurant_name)
        if not restaurant:
            raise NotFoundError(f"Restaurant '{restaurant_name}' not found")
        
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
    
    def get_restaurant_sections(self, restaurant_name: str) -> List[str]:
        """Get all section names for a restaurant."""
        restaurant = self.repository.get_by_name(restaurant_name)
        if not restaurant:
            raise NotFoundError(f"Restaurant '{restaurant_name}' not found")
        
        return [section.name for section in restaurant.sections]
    
    def get_section_items(self, restaurant_name: str, section_name: str) -> List[Dict[str, Any]]:
        """Get all items in a specific section."""
        # First check if restaurant exists
        restaurant = self.repository.get_by_name(restaurant_name)
        if not restaurant:
            raise NotFoundError(f"Restaurant '{restaurant_name}' not found")
        
        section = self.repository.get_section_by_name(restaurant_name, section_name)
        if not section:
            raise NotFoundError(f"Section '{section_name}' not found in restaurant '{restaurant_name}'")
        
        return [
            {
                "name": item.name,
                "description": item.description,
                "price": item.price
            }
            for item in section.items
        ]
    
    def get_restaurant_items(
        self,
        restaurant_name: str,
        price_gt: Optional[float] = None,
        price_lt: Optional[float] = None,
        sort_by: Optional[SortBy] = None,
        order: Order = Order.asc
    ) -> List[Dict[str, Any]]:
        """Get all items from a restaurant with filtering and sorting."""
        # Check if restaurant exists
        restaurant = self.repository.get_by_name(restaurant_name)
        if not restaurant:
            raise NotFoundError(f"Restaurant '{restaurant_name}' not found")
        
        # Get items with filtering
        items = self.repository.get_restaurant_items(restaurant_name, price_gt, price_lt)
        
        # Format response
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
        return sort_menu_items(result, sort_by, order)
    
    def get_restaurant_stats(self, restaurant_name: str) -> Dict[str, Any]:
        """Get statistics about a restaurant's menu."""
        return self.repository.get_restaurant_stats(restaurant_name)