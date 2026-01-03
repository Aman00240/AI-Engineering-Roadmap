from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, Integer
from database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self):
        return f"<Product(name={self.name}, price={self.price})>"
