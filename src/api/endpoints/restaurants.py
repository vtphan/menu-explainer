from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from src.services.restaurant_service import RestaurantService
from src.api.dependencies import get_restaurant_service
from src.utils.sorting import SortBy, Order
from src.core.exceptions import NotFoundError, restaurant_not_found, section_not_found

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.get("", response_model=List[str])
def get_restaurants(
    restaurant_service: RestaurantService = Depends(get_restaurant_service)
):
    """Return a list of all restaurant names."""
    return restaurant_service.get_all_restaurants()


@router.get("/{restaurant_name}")
def get_restaurant_menu(
    restaurant_name: str,
    restaurant_service: RestaurantService = Depends(get_restaurant_service)
):
    """Return the full menu for a specific restaurant."""
    try:
        return restaurant_service.get_restaurant_menu(restaurant_name)
    except NotFoundError:
        raise restaurant_not_found(restaurant_name)


@router.get("/{restaurant_name}/sections", response_model=List[str])
def get_restaurant_sections(
    restaurant_name: str,
    restaurant_service: RestaurantService = Depends(get_restaurant_service)
):
    """Return a list of all section names for a specific restaurant."""
    try:
        return restaurant_service.get_restaurant_sections(restaurant_name)
    except NotFoundError:
        raise restaurant_not_found(restaurant_name)


@router.get("/{restaurant_name}/sections/{section_name}")
def get_section_items(
    restaurant_name: str,
    section_name: str,
    restaurant_service: RestaurantService = Depends(get_restaurant_service)
):
    """Return all items in a specific section of a restaurant."""
    try:
        return restaurant_service.get_section_items(restaurant_name, section_name)
    except NotFoundError as e:
        if "Restaurant" in str(e):
            raise restaurant_not_found(restaurant_name)
        else:
            raise section_not_found(restaurant_name, section_name)


@router.get("/{restaurant_name}/items")
def get_restaurant_items(
    restaurant_name: str,
    price_gt: Optional[float] = Query(None, description="Filter items with price greater than"),
    price_lt: Optional[float] = Query(None, description="Filter items with price less than"),
    sort_by: Optional[SortBy] = Query(None, description="Sort items by name or price"),
    order: Order = Query(Order.asc, description="Sort order"),
    restaurant_service: RestaurantService = Depends(get_restaurant_service)
):
    """Return all items from a restaurant with optional filtering and sorting."""
    try:
        return restaurant_service.get_restaurant_items(
            restaurant_name, price_gt, price_lt, sort_by, order
        )
    except NotFoundError:
        raise restaurant_not_found(restaurant_name)