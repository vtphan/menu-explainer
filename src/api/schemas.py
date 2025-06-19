from pydantic import BaseModel
from typing import Optional, List
from src.utils.sorting import SortBy, Order


class MenuItemResponse(BaseModel):
    name: str
    description: Optional[str]
    price: Optional[float]
    section: str
    restaurant: str

    class Config:
        from_attributes = True


class MenuItemWithoutRestaurant(BaseModel):
    name: str
    description: Optional[str]
    price: Optional[float]
    section: Optional[str] = None

    class Config:
        from_attributes = True


class RestaurantStatsResponse(BaseModel):
    restaurant: str
    total_sections: int
    total_items: int
    items_with_price: int
    items_without_price: int
    average_price: Optional[float]
    min_price: Optional[float]
    max_price: Optional[float]


class SearchParams(BaseModel):
    query: Optional[str] = None
    price_gt: Optional[float] = None
    price_lt: Optional[float] = None
    restaurant: Optional[str] = None
    sort_by: Optional[SortBy] = None
    order: Order = Order.asc
    limit: int = 100


class PriceRangeParams(BaseModel):
    min_price: float
    max_price: float
    limit: int = 100


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None