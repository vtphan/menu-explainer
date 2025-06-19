"""
Tests for search API endpoints.
"""
import pytest
from tests.conftest import TestingSessionLocal
from src.models.database import Restaurant, Section, MenuItem


@pytest.fixture(scope="module")
def setup_database(test_db):
    """Set up test database with sample data."""
    
    # Add sample data
    db = TestingSessionLocal()
    try:
        # Create test restaurants
        restaurant1 = Restaurant(name="Pizza Place")
        restaurant2 = Restaurant(name="Burger Joint")
        db.add_all([restaurant1, restaurant2])
        db.flush()
        
        # Create sections
        section1 = Section(name="Pizzas", restaurant_id=restaurant1.id)
        section2 = Section(name="Burgers", restaurant_id=restaurant2.id)
        section3 = Section(name="Sides", restaurant_id=restaurant2.id)
        db.add_all([section1, section2, section3])
        db.flush()
        
        # Create menu items
        items = [
            MenuItem(name="Margherita Pizza", description="Fresh mozzarella and basil", price=14.99, section_id=section1.id),
            MenuItem(name="Pepperoni Pizza", description="Classic pepperoni", price=16.99, section_id=section1.id),
            MenuItem(name="Cheese Burger", description="Classic beef burger", price=12.99, section_id=section2.id),
            MenuItem(name="Chicken Burger", description="Grilled chicken breast", price=13.99, section_id=section2.id),
            MenuItem(name="French Fries", description="Crispy golden fries", price=4.99, section_id=section3.id),
            MenuItem(name="Onion Rings", description="Beer battered rings", price=5.99, section_id=section3.id),
        ]
        db.add_all(items)
        db.commit()
    finally:
        db.close()
    
    yield
    
    # Cleanup
    db = TestingSessionLocal()
    try:
        db.query(MenuItem).delete()
        db.query(Section).delete()
        db.query(Restaurant).delete()
        db.commit()
    finally:
        db.close()


def test_search_items(setup_database, test_client):
    """Test searching items across restaurants."""
    response = test_client.get("/search/items?query=pizza")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2  # Should find 2 pizza items
    for item in data:
        assert "pizza" in item["name"].lower()


def test_search_items_with_price_filter(setup_database, test_client):
    """Test searching items with price filters."""
    response = test_client.get("/search/items?price_gt=10&price_lt=15")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for item in data:
        assert 10 < item["price"] < 15


def test_search_items_by_restaurant(setup_database, test_client):
    """Test searching items filtered by restaurant."""
    response = test_client.get("/search/items?restaurant=Pizza Place")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2  # Pizza Place has 2 items
    for item in data:
        assert item["restaurant"] == "Pizza Place"


def test_search_items_with_sorting(setup_database, test_client):
    """Test searching items with sorting."""
    response = test_client.get("/search/items?sort_by=price&order=asc")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Check that prices are in ascending order
    prices = [item["price"] for item in data if item["price"] is not None]
    assert prices == sorted(prices)


def test_search_items_with_limit(setup_database, test_client):
    """Test searching items with result limit."""
    response = test_client.get("/search/items?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 3


def test_search_by_price_range(setup_database, test_client):
    """Test searching by price range."""
    response = test_client.get("/search/by-price-range?min_price=5&max_price=15")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for item in data:
        assert 5 <= item["price"] <= 15


def test_search_by_price_range_invalid(setup_database, test_client):
    """Test searching with invalid price range."""
    response = test_client.get("/search/by-price-range?min_price=20&max_price=10")
    assert response.status_code == 400
    data = response.json()
    assert "error" in data["detail"]


def test_find_restaurants_with_item(setup_database, test_client):
    """Test finding restaurants with specific item."""
    response = test_client.get("/search/restaurants-with-item?item_name=burger")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "Burger Joint" in data


def test_search_no_results(setup_database, test_client):
    """Test searching with no matching results."""
    response = test_client.get("/search/items?query=nonexistent")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0