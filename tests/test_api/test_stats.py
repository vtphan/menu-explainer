"""
Tests for statistics API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.models.database import Base, Restaurant, Section, MenuItem
from src.api.dependencies import get_database_session


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_stats_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_database_session] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    """Set up test database with sample data."""
    Base.metadata.create_all(bind=engine)
    
    # Add sample data
    db = TestingSessionLocal()
    try:
        # Create test restaurant
        restaurant = Restaurant(name="Stats Restaurant")
        db.add(restaurant)
        db.flush()
        
        # Create sections
        section1 = Section(name="Appetizers", restaurant_id=restaurant.id)
        section2 = Section(name="Main Courses", restaurant_id=restaurant.id)
        db.add_all([section1, section2])
        db.flush()
        
        # Create menu items with varied prices
        items = [
            MenuItem(name="Wings", description="Buffalo wings", price=8.99, section_id=section1.id),
            MenuItem(name="Nachos", description="Loaded nachos", price=12.99, section_id=section1.id),
            MenuItem(name="Steak", description="Grilled steak", price=28.99, section_id=section2.id),
            MenuItem(name="Salmon", description="Grilled salmon", price=24.99, section_id=section2.id),
            MenuItem(name="Special", description="Market price", price=None, section_id=section2.id),
        ]
        db.add_all(items)
        db.commit()
    finally:
        db.close()
    
    yield
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)


def test_get_restaurant_stats(setup_database):
    """Test getting restaurant statistics."""
    response = client.get("/stats/restaurant/Stats Restaurant")
    assert response.status_code == 200
    data = response.json()
    
    assert data["restaurant"] == "Stats Restaurant"
    assert data["total_sections"] == 2
    assert data["total_items"] == 5
    assert data["items_with_price"] == 4  # 4 items have prices
    assert data["items_without_price"] == 1  # 1 item without price
    assert data["min_price"] == 8.99
    assert data["max_price"] == 28.99
    assert data["average_price"] == round((8.99 + 12.99 + 28.99 + 24.99) / 4, 2)


def test_get_restaurant_stats_not_found(setup_database):
    """Test getting stats for nonexistent restaurant."""
    response = client.get("/stats/restaurant/Nonexistent Restaurant")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data["detail"]
    assert "not found" in data["detail"]["message"].lower()