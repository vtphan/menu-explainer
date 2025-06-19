from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.database import Restaurant, Section, MenuItem
from src.repositories.base import BaseRepository
from src.core.exceptions import NotFoundError


class RestaurantRepository(BaseRepository[Restaurant]):
    """Repository for restaurant-related database operations."""
    
    def __init__(self, db: Session):
        super().__init__(db, Restaurant)
    
    def get_by_name(self, name: str) -> Optional[Restaurant]:
        """Get restaurant by name."""
        return self.db.query(Restaurant).filter(Restaurant.name == name).first()
    
    def get_restaurant_with_sections(self, name: str) -> Optional[Restaurant]:
        """Get restaurant with all sections loaded."""
        return (
            self.db.query(Restaurant)
            .filter(Restaurant.name == name)
            .first()
        )
    
    def get_section_by_name(self, restaurant_name: str, section_name: str) -> Optional[Section]:
        """Get specific section from a restaurant."""
        return (
            self.db.query(Section)
            .join(Restaurant)
            .filter(Restaurant.name == restaurant_name, Section.name == section_name)
            .first()
        )
    
    def get_restaurant_items(
        self, 
        restaurant_name: str,
        price_gt: Optional[float] = None,
        price_lt: Optional[float] = None
    ) -> List[MenuItem]:
        """Get all items from a restaurant with optional price filtering."""
        query = (
            self.db.query(MenuItem)
            .join(Section)
            .join(Restaurant)
            .filter(Restaurant.name == restaurant_name)
        )
        
        if price_gt is not None:
            query = query.filter(MenuItem.price > price_gt)
        if price_lt is not None:
            query = query.filter(MenuItem.price < price_lt)
        
        return query.all()
    
    def search_items_across_restaurants(
        self,
        query_text: Optional[str] = None,
        price_gt: Optional[float] = None,
        price_lt: Optional[float] = None,
        restaurant_name: Optional[str] = None,
        limit: int = 100
    ) -> List[MenuItem]:
        """Search for items across all restaurants."""
        query = self.db.query(MenuItem).join(Section).join(Restaurant)
        
        if query_text:
            search_pattern = f"%{query_text}%"
            query = query.filter(
                (MenuItem.name.ilike(search_pattern)) | 
                (MenuItem.description.ilike(search_pattern))
            )
        
        if price_gt is not None:
            query = query.filter(MenuItem.price > price_gt)
        if price_lt is not None:
            query = query.filter(MenuItem.price < price_lt)
        
        if restaurant_name:
            query = query.filter(Restaurant.name == restaurant_name)
        
        return query.limit(limit).all()
    
    def get_items_by_price_range(
        self, 
        min_price: float, 
        max_price: float, 
        limit: int = 100
    ) -> List[MenuItem]:
        """Get items within a specific price range."""
        return (
            self.db.query(MenuItem)
            .join(Section)
            .join(Restaurant)
            .filter(MenuItem.price >= min_price, MenuItem.price <= max_price)
            .order_by(MenuItem.price)
            .limit(limit)
            .all()
        )
    
    def get_restaurants_with_item(self, item_name: str) -> List[Restaurant]:
        """Find restaurants that serve an item with the given name."""
        return (
            self.db.query(Restaurant)
            .join(Section)
            .join(MenuItem)
            .filter(MenuItem.name.ilike(f"%{item_name}%"))
            .distinct()
            .all()
        )
    
    def get_restaurant_stats(self, restaurant_name: str) -> dict:
        """Get statistics about a restaurant's menu."""
        restaurant = self.get_by_name(restaurant_name)
        if not restaurant:
            raise NotFoundError(f"Restaurant '{restaurant_name}' not found")
        
        # Get aggregated statistics
        stats = (
            self.db.query(
                func.count(MenuItem.id).label('total_items'),
                func.count(MenuItem.price).label('items_with_price'),
                func.avg(MenuItem.price).label('avg_price'),
                func.min(MenuItem.price).label('min_price'),
                func.max(MenuItem.price).label('max_price')
            )
            .join(Section)
            .filter(Section.restaurant_id == restaurant.id)
            .first()
        )
        
        return {
            "restaurant": restaurant_name,
            "total_sections": len(restaurant.sections),
            "total_items": stats.total_items or 0,
            "items_with_price": stats.items_with_price or 0,
            "items_without_price": (stats.total_items or 0) - (stats.items_with_price or 0),
            "average_price": round(stats.avg_price, 2) if stats.avg_price else None,
            "min_price": stats.min_price,
            "max_price": stats.max_price
        }