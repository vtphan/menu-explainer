"""
Tests for restaurant repository.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.repositories.restaurant_repository import RestaurantRepository
from src.models.database import Base, Restaurant, Section, MenuItem
from src.core.exceptions import NotFoundError


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_restaurant_repo.db"
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
    
    section1 = Section(name="Appetizers", restaurant_id=restaurant.id)
    section2 = Section(name="Main Courses", restaurant_id=restaurant.id)
    session.add_all([section1, section2])
    session.flush()
    
    items = [
        MenuItem(name="Wings", description="Buffalo wings", price=12.99, section_id=section1.id),
        MenuItem(name="Salad", description="Caesar salad", price=8.50, section_id=section1.id),
        MenuItem(name="Steak", description="Grilled steak", price=25.00, section_id=section2.id),
        MenuItem(name="Special", description="Market price", price=None, section_id=section2.id),
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


def test_get_by_name(db_session):
    """Test getting restaurant by name."""
    repo = RestaurantRepository(db_session)
    restaurant = repo.get_by_name("Test Restaurant")
    
    assert restaurant is not None
    assert restaurant.name == "Test Restaurant"


def test_get_by_name_not_found(db_session):
    """Test getting nonexistent restaurant by name."""
    repo = RestaurantRepository(db_session)
    restaurant = repo.get_by_name("Nonexistent Restaurant")
    
    assert restaurant is None


def test_get_restaurant_with_sections(db_session):
    """Test getting restaurant with sections loaded."""
    repo = RestaurantRepository(db_session)
    restaurant = repo.get_restaurant_with_sections("Test Restaurant")
    
    assert restaurant is not None
    assert len(restaurant.sections) == 2


def test_get_section_by_name(db_session):
    """Test getting section by restaurant and section name."""
    repo = RestaurantRepository(db_session)
    section = repo.get_section_by_name("Test Restaurant", "Appetizers")
    
    assert section is not None
    assert section.name == "Appetizers"


def test_get_restaurant_items(db_session):
    """Test getting all items from a restaurant."""
    repo = RestaurantRepository(db_session)
    items = repo.get_restaurant_items("Test Restaurant")
    
    assert isinstance(items, list)
    assert len(items) == 4


def test_get_restaurant_items_with_price_filter(db_session):
    """Test getting restaurant items with price filtering."""
    repo = RestaurantRepository(db_session)
    items = repo.get_restaurant_items("Test Restaurant", price_gt=10, price_lt=20)
    
    assert isinstance(items, list)
    # Should find Wings (12.99) but not Steak (25.00) or items without price
    filtered_items = [item for item in items if item.price and 10 < item.price < 20]
    assert len(filtered_items) >= 1


def test_search_items_across_restaurants(db_session):
    """Test searching items across all restaurants."""
    repo = RestaurantRepository(db_session)
    items = repo.search_items_across_restaurants(query_text="wings")
    
    assert isinstance(items, list)
    assert len(items) >= 1
    assert any("wings" in item.name.lower() for item in items)


def test_get_items_by_price_range(db_session):
    """Test getting items by price range."""
    repo = RestaurantRepository(db_session)
    items = repo.get_items_by_price_range(min_price=8, max_price=15)
    
    assert isinstance(items, list)
    for item in items:
        assert 8 <= item.price <= 15


def test_get_restaurants_with_item(db_session):
    """Test finding restaurants with specific item."""
    repo = RestaurantRepository(db_session)
    restaurants = repo.get_restaurants_with_item("wings")
    
    assert isinstance(restaurants, list)
    assert len(restaurants) >= 1
    assert any(r.name == "Test Restaurant" for r in restaurants)


def test_get_restaurant_stats(db_session):
    """Test getting restaurant statistics."""
    repo = RestaurantRepository(db_session)
    stats = repo.get_restaurant_stats("Test Restaurant")
    
    assert isinstance(stats, dict)
    assert stats["restaurant"] == "Test Restaurant"
    assert stats["total_sections"] == 2
    assert stats["total_items"] == 4
    assert stats["items_with_price"] == 3  # 3 items have prices
    assert stats["items_without_price"] == 1  # 1 item without price
    assert stats["min_price"] == 8.50
    assert stats["max_price"] == 25.00


def test_get_restaurant_stats_not_found(db_session):
    """Test getting stats for nonexistent restaurant."""
    repo = RestaurantRepository(db_session)
    
    with pytest.raises(NotFoundError):
        repo.get_restaurant_stats("Nonexistent Restaurant")