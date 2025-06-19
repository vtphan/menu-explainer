"""
Tests for restaurant service.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock

from src.services.restaurant_service import RestaurantService
from src.models.database import Base, Restaurant, Section, MenuItem
from src.core.exceptions import NotFoundError


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_service.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def setup_test_db():
    """Set up test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_test_db):
    """Create a database session for testing."""
    session = TestingSessionLocal()
    
    # Clean up any existing data
    session.query(MenuItem).delete()
    session.query(Section).delete()
    session.query(Restaurant).delete()
    session.commit()
    
    # Add test data
    restaurant = Restaurant(name="Test Restaurant")
    session.add(restaurant)
    session.flush()
    
    section = Section(name="Test Section", restaurant_id=restaurant.id)
    session.add(section)
    session.flush()
    
    item = MenuItem(name="Test Item", description="Test Description", price=12.99, section_id=section.id)
    session.add(item)
    session.commit()
    
    yield session
    
    # Clean up after test
    session.query(MenuItem).delete()
    session.query(Section).delete()
    session.query(Restaurant).delete()
    session.commit()
    session.close()


def test_get_all_restaurants(db_session):
    """Test getting all restaurant names."""
    service = RestaurantService(db_session)
    restaurants = service.get_all_restaurants()
    assert isinstance(restaurants, list)
    assert "Test Restaurant" in restaurants


def test_get_restaurant_menu(db_session):
    """Test getting restaurant menu."""
    service = RestaurantService(db_session)
    menu = service.get_restaurant_menu("Test Restaurant")
    
    assert isinstance(menu, dict)
    assert "Test Section" in menu
    assert len(menu["Test Section"]) == 1
    assert menu["Test Section"][0]["name"] == "Test Item"


def test_get_nonexistent_restaurant_menu(db_session):
    """Test getting menu for nonexistent restaurant."""
    service = RestaurantService(db_session)
    
    with pytest.raises(NotFoundError):
        service.get_restaurant_menu("Nonexistent Restaurant")


def test_get_restaurant_sections(db_session):
    """Test getting restaurant sections."""
    service = RestaurantService(db_session)
    sections = service.get_restaurant_sections("Test Restaurant")
    
    assert isinstance(sections, list)
    assert "Test Section" in sections


def test_get_section_items(db_session):
    """Test getting section items."""
    service = RestaurantService(db_session)
    items = service.get_section_items("Test Restaurant", "Test Section")
    
    assert isinstance(items, list)
    assert len(items) == 1
    assert items[0]["name"] == "Test Item"
    assert items[0]["price"] == 12.99


def test_get_restaurant_items(db_session):
    """Test getting all restaurant items."""
    service = RestaurantService(db_session)
    items = service.get_restaurant_items("Test Restaurant")
    
    assert isinstance(items, list)
    assert len(items) >= 1
    assert items[0]["name"] == "Test Item"
    assert items[0]["section"] == "Test Section"