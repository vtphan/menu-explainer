# Menu Explainer API

A FastAPI-based REST API with modular architecture that serves restaurant menu data from a SQLite database. The API provides endpoints to browse restaurant menus, sections, and items with filtering and sorting capabilities, plus cross-restaurant search functionality.

## Features

- **Restaurant Menu Browsing**: View menus by restaurant and section
- **Cross-Restaurant Search**: Search for items across all restaurants
- **Price Filtering**: Filter items by price ranges
- **Sorting**: Sort results by name or price
- **Statistics**: Get analytics about restaurant menus
- **Modular Architecture**: Clean separation of concerns with layered design
- **SQLite Database**: Persistent data storage with optimized queries
- **Interactive API Docs**: Swagger UI and ReDoc documentation

## Quick Start

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Installation

1. Clone the repository and navigate to the project directory
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Database Setup

Build the database from the provided JSON file:
```bash
python cli.py build menus.json
```

### Run the Server

Start the API server using one of these methods:

**Option 1: Using the CLI tool (recommended)**
```bash
python cli.py serve
```

**Option 2: Using uvicorn directly**
```bash
uvicorn main:app --reload
```

**Option 3: Run on a different port**
```bash
uvicorn main:app --reload --port 8080
```

The API will be available at `http://localhost:8000` (or the specified port)

### API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Restaurant Endpoints

- `GET /restaurants` - List all restaurant names
- `GET /restaurants/{name}` - Get full menu for a restaurant
- `GET /restaurants/{name}/sections` - Get section names for a restaurant
- `GET /restaurants/{name}/sections/{section}` - Get items in a specific section
- `GET /restaurants/{name}/items` - Get all items with filtering and sorting

### Search Endpoints

- `GET /search/items` - Search items across all restaurants
- `GET /search/by-price-range` - Find items within a price range
- `GET /search/restaurants-with-item` - Find restaurants serving a specific item

### Statistics Endpoints

- `GET /stats/restaurant/{name}` - Get statistics about a restaurant's menu

## Example Usage

```bash
# List all restaurants
curl http://localhost:8000/restaurants

# Get a restaurant's full menu
curl http://localhost:8000/restaurants/Acre

# Search for chicken dishes under $30
curl "http://localhost:8000/search/items?query=chicken&price_lt=30"

# Find items between $10-20 across all restaurants
curl "http://localhost:8000/search/by-price-range?min_price=10&max_price=20"

# Get restaurant statistics
curl http://localhost:8000/stats/restaurant/Acre
```

## Architecture

The application follows a layered architecture pattern:

```
src/
├── api/           # API layer - FastAPI endpoints and routing
│   ├── endpoints/ # Route handlers split by domain
│   ├── schemas.py # Pydantic models for request/response
│   └── dependencies.py # FastAPI dependency injection
├── services/      # Business logic layer
├── repositories/  # Data access layer
├── models/        # Database models and schemas
├── core/          # Configuration and exceptions
└── utils/         # Shared utilities
```

### Key Benefits

- **Maintainability**: Each layer has a single responsibility
- **Testability**: Layers can be tested independently
- **Extensibility**: Easy to add new features
- **Flexibility**: Can swap implementations easily

## Configuration

Copy `.env.example` to `.env` and modify as needed:

```bash
cp .env.example .env
```

Available configuration options:
- `DATABASE_URL`: SQLite database file path
- `HOST`/`PORT`: Server host and port (PORT is automatically set by Render in production)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `DEBUG`: Enable debug mode

### Deployment on Render

The application is configured to work with [Render](https://render.com) out of the box:

1. Push your code to GitHub
2. Connect your GitHub repo to Render
3. Render will automatically:
   - Run `./build.sh` to install dependencies and build the database
   - Start the server on the correct port using the `PORT` environment variable

The app automatically uses `PORT` environment variable when available (Render) or falls back to port 8000 for local development.

## Development

### Adding New Endpoints

1. Create route handlers in `src/api/endpoints/`
2. Add business logic to `src/services/`
3. Add database operations to `src/repositories/`
4. Update the main app to include new routers

### Database Schema

The database consists of three main tables:
- `restaurants`: Restaurant information
- `sections`: Menu sections within restaurants
- `menu_items`: Individual menu items with prices and descriptions

## Data Format

The application expects JSON data in this format:

```json
{
  "restaurant_name": {
    "sections": [
      {
        "name": "Section Name",
        "items": [
          {
            "name": "Item Name",
            "description": "Item description",
            "price": 12.99
          }
        ]
      }
    ]
  }
}
```

## License

This project is licensed under the MIT License.