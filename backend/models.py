"""Database models and Pydantic schemas for DictaMeal recipes."""
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel
from typing import Optional, List

SQLALCHEMY_DATABASE_URL = "sqlite:///./recipes.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class RecipeDB(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    ingredients = Column(Text)  # JSON stored as string for simplicity in MVP
    steps = Column(Text)  # JSON stored as string
    duration = Column(String, nullable=True)
    origin = Column(String, nullable=True)
    meal_type = Column(String, nullable=True)
    original_transcription = Column(Text, nullable=True)
    image_data = Column(Text, nullable=True)


# Pydantic models
class RecipeBase(BaseModel):
    title: str
    description: Optional[str] = None
    ingredients: List[str]
    steps: List[str]
    duration: Optional[str] = None
    origin: Optional[str] = None
    meal_type: Optional[str] = None
    original_transcription: Optional[str] = None
    image_data: Optional[str] = None


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(RecipeBase):
    pass


class Recipe(RecipeBase):
    id: int

    class Config:
        from_attributes = True
