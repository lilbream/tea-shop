from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.models.models import Category, Product
from backend.models.database import get_db

router = APIRouter()

@router.get("/main-categories")
async def get_main_categories(db: Session = Depends(get_db)):
    return db.query(Category).filter(Category.is_main == True).all()

@router.get("/category/{category_id}")
async def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.get("/category/{category_id}/products")
async def get_category_products(category_id: int, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.category_id == category_id).all()

@router.get("/products/featured")
async def get_featured_products(db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.featured == True).limit(5).all()