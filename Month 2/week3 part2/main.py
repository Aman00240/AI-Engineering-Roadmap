from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from models import Product, CartItem
from database import get_db, engine, Base
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating Database tables")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    print("Shutting Down")


app = FastAPI(lifespan=lifespan)


class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int

    @field_validator("name")
    def check_name_empty(cls, v: str) -> str:
        v = v.strip().title()

        if not v:
            raise ValueError("Asset name cannot be empty")

        if len(v) < 2:
            raise ValueError("Asset name must be at least 2 characters")

        if v.isdigit():
            raise ValueError("Asset name cannot be just numbers")

        return v

    @field_validator("price")
    def check_price(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Asset Price cant be negative")

        return v


class CartAdd(BaseModel):
    product_id: int
    quantity: int


@app.get("/products")
async def get_products(db: AsyncSession = Depends(get_db)):
    query = select(Product)

    result = await db.execute(query)

    products = result.scalars().all()

    return products


@app.get("/cart")
async def get_cart(db: AsyncSession = Depends(get_db)):
    query = select(CartItem).options(joinedload(CartItem.product))

    result = await db.execute(query)

    items = result.scalars().all()

    return items


@app.post("/add_product")
async def add_asset(item: ProductCreate, db: AsyncSession = Depends(get_db)):
    new_product = Product(name=item.name, price=item.price, stock=item.stock)

    db.add(new_product)

    await db.commit()
    await db.refresh(new_product)

    return new_product


@app.post("/cart")
async def add_to_cart(item: CartAdd, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, item.product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product Not Found")

    if product.stock < item.quantity:
        raise HTTPException(status_code=400, detail="Not enough Stock")

    new_cart_item = CartItem(product_id=item.product_id, quantity=item.quantity)

    db.add(new_cart_item)

    product.stock -= item.quantity

    await db.commit()
    await db.refresh(new_cart_item)

    return {"message": "Cart Updated", "cart_item_id": new_cart_item.id}
