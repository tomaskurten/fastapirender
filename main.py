from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "sqlite:///./test.db"

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class ProductDB(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Product(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True  # Allows Pydantic to work with SQLAlchemy objects

@app.get("/")
def message():
    return "holaa"

@app.get("/products", response_model=List[Product])
def get_products(db: Session = Depends(get_db)):
    products = db.query(ProductDB).all()
    return products

@app.get("/products/{id}", response_model=Product)
def get_product(id: int, db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id == id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/products", response_model=Product)
def create_product(product: Product, db: Session = Depends(get_db)):
    db_product = db.query(ProductDB).filter(ProductDB.id == product.id).first()
    if db_product:
        raise HTTPException(status_code=400, detail="Product with this ID already exists")
    new_product = ProductDB(id=product.id, name=product.name)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product