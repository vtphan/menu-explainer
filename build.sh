#!/usr/bin/env bash
# Build script for Render deployment

echo "Starting build process..."

# Install Python dependencies
echo "Installing requirements..."
pip install -r requirements.txt

# Build the database from menus.json
echo "Building database..."
python cli.py build menus.json

echo "Build complete!"