from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pathlib import Path
import os
import shutil
from backend.models.database import SessionLocal, engine
from backend.models.models import Base, Category, Product

# Настройка пути к SQLite (специально для Railway)
DATA_DIR = Path("/data")  # Railway разрешает запись только в /data
DATA_DIR.mkdir(exist_ok=True, parents=True)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATA_DIR}/database.db"

# Переопределяем engine с новым путём
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

app = FastAPI()

# Раздача статики (только в продакшене)
if os.getenv("RAILWAY_ENVIRONMENT"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Роутеры
from backend.routers import products, cart
app.include_router(products.router, prefix="/api")
app.include_router(cart.router, prefix="/api")

@app.on_event("startup")
async def startup():
    # Создаём таблицы
    Base.metadata.create_all(bind=engine)
    
    # Тестовые данные
    db = SessionLocal()
    try:
        if not db.query(Category).first():
            tea = Category(name="Чай", is_main=True)
            dish = Category(name="Посуда", is_main=True)
            
            db.add_all([tea, dish])
            db.commit()
            db.refresh(tea)
            db.refresh(dish)
            
            subcats = [
                Category(name="Шу Пуэр", parent_id=tea.id),
                Category(name="Шен Пуэр", parent_id=tea.id),
                Category(name="Доски", parent_id=dish.id)
            ]
            
            test_products = [
                Product(
                    name="Шу Пуэр 'Старый лес'", 
                    description="Выдержка 5 лет", 
                    image_url="/static/images/puer.jpg",
                    price=2990,
                    stock=10,
                    category_id=subcats[0].id,
                    featured=True
                )
            ]
            
            db.add_all(subcats + test_products)
            db.commit()
    finally:
        db.close()

# Эндпоинт для резервного копирования (важно для Railway)
@app.get("/backup")
async def create_backup(background_tasks: BackgroundTasks):
    if not DATA_DIR.exists():
        return {"error": "Data directory not found"}
    
    backup_path = DATA_DIR / "backup.db"
    background_tasks.add_task(
        shutil.copy,
        DATA_DIR / "database.db",
        backup_path
    )
    return {"status": f"Backup started at {backup_path}"}

# Проверка работоспособности
@app.get("/health")
async def health_check():
    return {
        "status": "OK",
        "database": str(DATA_DIR / "database.db"),
        "files": os.listdir(DATA_DIR) if DATA_DIR.exists() else "No data dir"
    }