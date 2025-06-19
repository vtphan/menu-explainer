import json
import sys
import argparse
from src.models.database import create_tables, drop_tables, get_db, Restaurant, Section, MenuItem


def build_database(json_file: str):
    """Build the SQLite database from a JSON file."""
    print(f"Building database from {json_file}...")
    
    try:
        with open(json_file, 'r') as f:
            menu_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {json_file} not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {json_file}.")
        sys.exit(1)
    
    # Drop existing tables and recreate
    print("Dropping existing tables...")
    drop_tables()
    print("Creating new tables...")
    create_tables()
    
    # Import data
    with get_db() as db:
        for restaurant_name, restaurant_data in menu_data.items():
            print(f"Importing restaurant: {restaurant_name}")
            
            # Create restaurant
            restaurant = Restaurant(name=restaurant_name)
            db.add(restaurant)
            db.flush()  # Flush to get the ID
            
            # Get sections array from restaurant data
            sections = restaurant_data.get("sections", [])
            
            # Create sections and items
            for section_data in sections:
                section_name = section_data.get("name", "")
                section = Section(name=section_name, restaurant_id=restaurant.id)
                db.add(section)
                db.flush()
                
                # Create menu items
                items = section_data.get("items", [])
                for item_data in items:
                    # Handle price - convert to float or None if not a valid number
                    price = item_data.get("price")
                    if price is not None:
                        try:
                            price = float(price)
                        except (ValueError, TypeError):
                            # If price is not a valid number (e.g., "MKT"), set to None
                            price = None
                    
                    menu_item = MenuItem(
                        name=item_data.get("name", ""),
                        description=item_data.get("description"),
                        price=price,
                        section_id=section.id
                    )
                    db.add(menu_item)
            
            db.commit()
            print(f"  - Imported {len(sections)} sections")
    
        print("Database build complete!")


def serve():
    """Start the FastAPI server."""
    import uvicorn
    from src.core.config import settings
    print("Starting FastAPI server...")
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )


def main():
    parser = argparse.ArgumentParser(description="Menu Explainer CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build database from JSON file")
    build_parser.add_argument("json_file", help="Path to JSON file containing menu data")
    
    # Serve command
    subparsers.add_parser("serve", help="Start the API server")
    
    args = parser.parse_args()
    
    if args.command == "build":
        build_database(args.json_file)
    elif args.command == "serve":
        serve()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()