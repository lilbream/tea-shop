from models.database import engine, Base
from models.models import Category, Product

Base.metadata.create_all(bind=engine)