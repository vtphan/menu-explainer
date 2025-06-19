from abc import ABC, abstractmethod
from typing import List, Optional, Generic, TypeVar, Type
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeclarativeMeta

T = TypeVar('T')


class BaseRepository(Generic[T], ABC):
    """Base repository class providing common CRUD operations."""
    
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get a single record by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination."""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, obj: T) -> T:
        """Create a new record."""
        self.db.add(obj)
        self.db.flush()
        return obj
    
    def update(self, obj: T) -> T:
        """Update an existing record."""
        self.db.merge(obj)
        self.db.flush()
        return obj
    
    def delete(self, obj: T) -> None:
        """Delete a record."""
        self.db.delete(obj)
        self.db.flush()
    
    def count(self) -> int:
        """Get total count of records."""
        return self.db.query(self.model).count()