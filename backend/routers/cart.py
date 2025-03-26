from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.models.models import CartItem, Product
from backend.models.database import get_db

router = APIRouter()

@router.post("/cart/add")
async def add_to_cart(
    product_id: int, 
    quantity: int = 1,
    user_id: int = 1,  # Временное решение до реализации аутентификации
    db: Session = Depends(get_db)
):
    # Проверяем существует ли продукт
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Проверяем есть ли уже такой товар в корзине
    cart_item = db.query(CartItem).filter(
        CartItem.product_id == product_id,
        CartItem.user_id == user_id
    ).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            product_id=product_id,
            quantity=quantity,
            user_id=user_id
        )
        db.add(cart_item)
    
    db.commit()
    return {"status": "success", "product_id": product_id}

@router.get("/cart/{user_id}")
async def get_cart(user_id: int, db: Session = Depends(get_db)):
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    return cart_items