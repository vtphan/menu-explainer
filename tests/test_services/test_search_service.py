"""
Tests for search service.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.services.search_service import SearchService
from src.models.database import Base, Restaurant, Section, MenuItem
from src.core.exceptions import ValidationError
from src.utils.sorting import SortBy, Order


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_search_service.db"
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
    restaurant1 = Restaurant(name="Restaurant 1")
    restaurant2 = Restaurant(name="Restaurant 2")
    session.add_all([restaurant1, restaurant2])
    session.flush()
    
    section1 = Section(name="Appetizers", restaurant_id=restaurant1.id)
    section2 = Section(name="Main Courses", restaurant_id=restaurant1.id)
    section3 = Section(name="Appetizers", restaurant_id=restaurant2.id)
    session.add_all([section1, section2, section3])
    session.flush()
    
    # Create test menu items
    items = [
        MenuItem(name="Chicken Wings", description="Spicy buffalo wings", price=12.99, section_id=section1.id),
        MenuItem(name="Caesar Salad", description="Fresh romaine lettuce", price=8.50, section_id=section1.id),
        MenuItem(name="Grilled Chicken", description="Herb crusted chicken breast", price=18.99, section_id=section2.id),
        MenuItem(name="Fish Tacos", description="Fresh fish with spicy sauce", price=15.75, section_id=section2.id),
        MenuItem(name="Chicken Quesadilla", description="Grilled chicken and cheese", price=11.25, section_id=section3.id),
    ]
    session.add_all(items)
    session.commit()
    
    yield session
    
    # Clean up after test
    session.query(MenuItem).delete()
    session.query(Section).delete()
    session.query(Restaurant).delete()
    session.commit()
    session.close()


def test_search_items_by_query(db_session):
    """Test searching items by query text."""
    service = SearchService(db_session)
    results = service.search_items(query="chicken")
    
    assert isinstance(results, list)
    assert len(results) == 3  # Should find 3 chicken items
    for item in results:
        assert "chicken" in item["name"].lower() or "chicken" in (item["description"] or "").lower()


def test_search_items_by_price_filter(db_session):
    """Test searching items with price filters."""
    service = SearchService(db_session)
    results = service.search_items(price_gt=10, price_lt=15)
    
    assert isinstance(results, list)
    # Should find items between $10-15
    for item in results:
        assert 10 < item["price"] < 15


def test_search_items_by_restaurant(db_session):
    """Test searching items filtered by restaurant."""
    service = SearchService(db_session)
    results = service.search_items(restaurant="Restaurant 1")
    
    assert isinstance(results, list)
    assert len(results) == 4  # Restaurant 1 has 4 items
    for item in results:
        assert item["restaurant"] == "Restaurant 1"


def test_search_items_with_sorting(db_session):
    """Test searching items with sorting."""
    service = SearchService(db_session)
    results = service.search_items(sort_by=SortBy.price, order=Order.asc)
    
    assert isinstance(results, list)
    # Check that prices are in ascending order (ignoring None values)
    prices = [item["price"] for item in results if item["price"] is not None]
    assert prices == sorted(prices)


def test_search_by_price_range(db_session):
    """Test searching by price range."""
    service = SearchService(db_session)
    results = service.search_by_price_range(min_price=10, max_price=16)
    
    assert isinstance(results, list)
    for item in results:
        assert 10 <= item["price"] <= 16


def test_search_by_price_range_invalid(db_session):
    """Test searching with invalid price range."""
    service = SearchService(db_session)
    
    with pytest.raises(ValidationError):
        service.search_by_price_range(min_price=20, max_price=10)


def test_find_restaurants_with_item(db_session):
    """Test finding restaurants that serve a specific item."""
    service = SearchService(db_session)
    results = service.find_restaurants_with_item("chicken")
    
    assert isinstance(results, list)
    assert len(results) == 2  # Both restaurants have chicken items
    assert "Restaurant 1" in results
    assert "Restaurant 2" in results


def test_search_items_no_results(db_session):
    """Test searching with no matching results."""
    service = SearchService(db_session)
    results = service.search_items(query="nonexistent")
    
    assert isinstance(results, list)
    assert len(results) == 0


def test_search_items_with_limit(db_session):
    """Test searching with result limit."""
    service = SearchService(db_session)
    results = service.search_items(limit=2)
    
    assert isinstance(results, list)
    assert len(results) <= 2