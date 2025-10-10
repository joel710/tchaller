from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db, Category
from ..schemas import Category as CategorySchema, CategoryCreate
from typing import List

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=List[CategorySchema])
async def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    categories = db.query(Category).all()
    return categories

@router.post("/", response_model=CategorySchema)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new category"""
    category = Category(name=category_data.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category