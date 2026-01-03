from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

app = FastAPI()

inventory = {
    1: {"name": "Laptop", "price": 999.99, "stock": 5},
    2: {"name": "Mouse", "price": 25.50, "stock": 10},
    3: {"name": "Keyboard", "price": 45.00, "stock": 2},
    4: {"name": "Monitor", "price": 150.00, "stock": 0},
}


# The user's cart Format: {product_id: quantity}
cart = {}


class CartItem(BaseModel):
    product_id: int
    quantity: int

    @field_validator("product_id")
    def check_product_id(cls, p):
        if p <= 0:
            raise ValueError("product id cant be 0 or negative")

        return p

    @field_validator("quantity")
    def check_quantity(cls, q):
        if q <= 0:
            raise ValueError("quantity cant be 0 or negative")

        return q


class CartUpdate(BaseModel):
    quantity: int

    @field_validator("quantity")
    def check_quantity(cls, q):
        if q <= 0:
            raise ValueError("quantity cant be 0 or negative")

        return q


@app.get("/products")
async def get_products(min_price: float | None = None):
    results = {}

    if min_price:
        for product_id, details in inventory.items():
            if details["price"] > min_price:
                results[product_id] = details

        return results

    return inventory


@app.get("/product/{product_id}")
async def get_product_details(product_id: int):
    if product_id in inventory:
        return inventory[product_id]

    raise HTTPException(status_code=404, detail="Item Not Found")


@app.post("/cart")
async def add_to_cart(item: CartItem):
    if item.product_id not in inventory:
        raise HTTPException(status_code=404, detail="Product Id Not Found")

    if inventory[item.product_id]["stock"] < item.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock available")

    cart[item.product_id] = item.quantity
    return {"message": "Added to cart", "cart": cart}


@app.put("/cart/{item_id}")
async def update_cart_quantity(item_id: int, update_data: CartUpdate):
    new_quantity = update_data.quantity

    if item_id not in cart:
        raise HTTPException(status_code=404, detail="Item not in cart")

    if item_id not in inventory:
        raise HTTPException(status_code=404, detail="Item not in found in shop")

    item_stock = inventory[item_id]["stock"]

    if new_quantity > item_stock:
        raise HTTPException(status_code=400, detail="Not enough stock available")

    cart[item_id] = new_quantity

    return {"message": "Cart updated", "cart": cart}


@app.delete("/cart/{item_id}")
async def delete_item_from_cart(item_id: int):
    if item_id not in cart:
        raise HTTPException(status_code=404, detail="Item not in cart")

    del cart[item_id]

    return {"message": "Item Removed Sucessfully", "Cart": cart}


@app.delete("/checkout")
async def cart_checkout():
    sum = 0

    for id in cart.keys():
        price = inventory[id]["price"]

        sum += price * cart[id]

        inventory[id]["stock"] = inventory[id]["stock"] - cart[id]

    cart.clear()

    return {"total_paid": sum, "message": "Order Successful"}
