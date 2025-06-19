"""
Tests for restaurant API endpoints.
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
        # Clean existing data
        db.query(MenuItem).delete()
        db.query(Section).delete()
        db.query(Restaurant).delete()
        db.commit()
        
        # Create a test restaurant
        restaurant = Restaurant(name="Test Restaurant")
        db.add(restaurant)
        db.flush()
        
        # Create a test section
        section = Section(name="Test Section", restaurant_id=restaurant.id)
        db.add(section)
        db.flush()
        
        # Create test menu items
        item1 = MenuItem(name="Test Item 1", description="Description 1", price=10.99, section_id=section.id)
        item2 = MenuItem(name="Test Item 2", description="Description 2", price=15.50, section_id=section.id)
        db.add_all([item1, item2])
        
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


def test_get_restaurants(setup_database, test_client):
    """Test getting all restaurants."""
    response = test_client.get("/restaurants")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "Test Restaurant" in data


def test_get_restaurant_menu(setup_database, test_client):
    """Test getting restaurant menu."""
    response = test_client.get("/restaurants/Test Restaurant")
    assert response.status_code == 200
    data = response.json()
    assert "Test Section" in data
    assert len(data["Test Section"]) == 2


def test_get_restaurant_sections(setup_database, test_client):
    """Test getting restaurant sections."""
    response = test_client.get("/restaurants/Test Restaurant/sections")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "Test Section" in data


def test_get_section_items(setup_database, test_client):
    """Test getting section items."""
    response = test_client.get("/restaurants/Test Restaurant/sections/Test Section")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["name"] in ["Test Item 1", "Test Item 2"]


def test_get_restaurant_items(setup_database, test_client):
    """Test getting all restaurant items."""
    response = test_client.get("/restaurants/Test Restaurant/items")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_get_nonexistent_restaurant(test_client):
    """Test getting nonexistent restaurant."""
    response = test_client.get("/restaurants/Nonexistent Restaurant")
    assert response.status_code == 404


def test_root_endpoint(test_client):
    """Test root endpoint."""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data