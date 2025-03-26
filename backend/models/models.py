from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    is_main = Column(Boolean, default=False)
    
    children = relationship("Category")
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    image_url = Column(String(500), nullable=False)
    price = Column(Integer, nullable=False)
    stock = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey('categories.id'))
    featured = Column(Boolean, default=False)
    
    category = relationship("Category", back_populates="products")

class CartItem(Base):
    __tablename__ = 'cart_items'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, default=1)
    user_id = Column(Integer)
    
    product = relationship("Product")