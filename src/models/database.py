from sqlalchemy import create_engine, Column, Integer, String, Text, Float, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from contextlib import contextmanager
from src.core.config import settings

Base = declarative_base()

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    
    sections = relationship("Section", back_populates="restaurant", cascade="all, delete-orphan")


class Section(Base):
    __tablename__ = "sections"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    
    restaurant = relationship("Restaurant", back_populates="sections")
    items = relationship("MenuItem", back_populates="section", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_section_restaurant", "restaurant_id", "name"),
    )


class MenuItem(Base):
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    
    section = relationship("Section", back_populates="items")
    
    __table_args__ = (
        Index("idx_item_price", "price"),
        Index("idx_item_name", "name"),
        Index("idx_item_section", "section_id"),
    )


def create_tables():
    Base.metadata.create_all(bind=engine)


def drop_tables():
    Base.metadata.drop_all(bind=engine)


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()