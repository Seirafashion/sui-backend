from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    products: Mapped[List["Product"]] = relationship(back_populates="category")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "product_count": len(self.products),
        }


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[float] = mapped_column(Float(asdecimal=False), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    image_url: Mapped[str] = mapped_column(Text, default="")
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))

    category: Mapped[Category] = relationship(back_populates="products")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "imageUrl": self.image_url,
            "category": {
                "id": self.category.id,
                "name": self.category.name,
                "slug": self.category.slug,
            },
        }


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    customer_email: Mapped[str] = mapped_column(String(200), nullable=False)
    shipping_address: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="processing")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "shipping_address": self.shipping_address,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "items": [item.to_dict() for item in self.items],
            "total": sum(item.quantity * item.unit_price for item in self.items),
        }


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float(asdecimal=False), nullable=False)

    order: Mapped[Order] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()

    def to_dict(self) -> dict:
        return {
            "product": {
                "id": self.product.id,
                "name": self.product.name,
            },
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "subtotal": self.quantity * self.unit_price,
        }
