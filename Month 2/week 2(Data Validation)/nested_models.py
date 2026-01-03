from pydantic import BaseModel, Field


class Address(BaseModel):
    city: str = Field(min_length=2)
    zip: str = Field(min_length=2)


class Product(BaseModel):
    name: str = Field(min_length=2)
    price: float = Field(gt=0)


class Order(BaseModel):
    order_id: int = Field(gt=0)
    address: Address
    items: list[Product]


address1 = Address(city="Youyou", zip="1234")
product1 = Product(name="laptop", price=1200.90)
product2 = Product(name="phone", price=14200.90)

order1 = Order(order_id=1, address=address1, items=[product1, product2])
print(order1.items[0].name)
print(order1.items[1].name)
