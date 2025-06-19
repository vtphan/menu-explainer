from fastapi import FastAPI
from src.core.config import settings
from src.core.logging import setup_logging
from src.api.endpoints import restaurants, search, stats, privacy

# Setup logging
setup_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API to browse restaurant menus with SQLite backend and cross-restaurant search",
)

# Include routers
app.include_router(restaurants.router)
app.include_router(search.router)
app.include_router(stats.router)
app.include_router(privacy.router)


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the Menu Explainer API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port, debug=settings.debug)