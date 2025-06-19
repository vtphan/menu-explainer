from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from src.services.search_service import SearchService
from src.api.dependencies import get_search_service
from src.api.schemas import MenuItemResponse
from src.utils.sorting import SortBy, Order
from src.core.exceptions import ValidationError, validation_error

router = APIRouter(prefix="/search", tags=["Cross-Restaurant Search"])


@router.get("/items", response_model=List[MenuItemResponse])
def search_items(
    query: Optional[str] = Query(None, description="Search in item names and descriptions"),
    price_gt: Optional[float] = Query(None, description="Filter items with price greater than"),
    price_lt: Optional[float] = Query(None, description="Filter items with price less than"),
    restaurant: Optional[str] = Query(None, description="Filter by restaurant name"),
    sort_by: Optional[SortBy] = Query(None, description="Sort items by name or price"),
    order: Order = Query(Order.asc, description="Sort order"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
    search_service: SearchService = Depends(get_search_service)
):
    """Search for menu items across all restaurants."""
    results = search_service.search_items(
        query=query,
        price_gt=price_gt,
        price_lt=price_lt,
        restaurant=restaurant,
        sort_by=sort_by,
        order=order,
        limit=limit
    )
    
    return [MenuItemResponse(**item) for item in results]


@router.get("/by-price-range", response_model=List[MenuItemResponse])
def search_by_price_range(
    min_price: float = Query(..., ge=0, description="Minimum price"),
    max_price: float = Query(..., ge=0, description="Maximum price"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
    search_service: SearchService = Depends(get_search_service)
):
    """Find all items within a specific price range across all restaurants."""
    try:
        results = search_service.search_by_price_range(min_price, max_price, limit)
        return [MenuItemResponse(**item) for item in results]
    except ValidationError as e:
        raise validation_error(str(e))


@router.get("/restaurants-with-item", response_model=List[str])
def find_restaurants_with_item(
    item_name: str = Query(..., description="Item name to search for (case-insensitive)"),
    search_service: SearchService = Depends(get_search_service)
):
    """Find all restaurants that have an item with the given name."""
    return search_service.find_restaurants_with_item(item_name)