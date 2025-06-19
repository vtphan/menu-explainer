from fastapi import APIRouter, Depends
from src.services.restaurant_service import RestaurantService
from src.api.dependencies import get_restaurant_service
from src.api.schemas import RestaurantStatsResponse
from src.core.exceptions import NotFoundError, restaurant_not_found

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/restaurant/{restaurant_name}", response_model=RestaurantStatsResponse)
def get_restaurant_stats(
    restaurant_name: str,
    restaurant_service: RestaurantService = Depends(get_restaurant_service)
):
    """Get statistics about a restaurant's menu."""
    try:
        stats = restaurant_service.get_restaurant_stats(restaurant_name)
        return RestaurantStatsResponse(**stats)
    except NotFoundError:
        raise restaurant_not_found(restaurant_name)