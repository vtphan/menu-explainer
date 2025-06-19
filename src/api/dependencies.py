from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.services.restaurant_service import RestaurantService
from src.services.search_service import SearchService
from src.core.exceptions import NotFoundError, ValidationError


def get_database_session() -> Session:
    """FastAPI dependency to get database session."""
    with get_db() as db:
        yield db


def get_restaurant_service(db: Session = Depends(get_database_session)) -> RestaurantService:
    """FastAPI dependency to get restaurant service."""
    return RestaurantService(db)


def get_search_service(db: Session = Depends(get_database_session)) -> SearchService:
    """FastAPI dependency to get search service."""
    return SearchService(db)


def handle_service_exceptions(func):
    """Decorator to handle service layer exceptions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")
    return wrapper