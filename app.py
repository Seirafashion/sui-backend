from __future__ import annotations

from typing import Any

from flask import Flask, abort, jsonify, redirect, request, send_from_directory, url_for
from sqlalchemy import Select, func, select
from sqlalchemy.orm import joinedload

from . import config
from .database import Base, engine, session_scope
from .models import Category, Order, OrderItem, Product


def create_app() -> Flask:
    app = Flask(
        __name__,
        static_folder=str(config.ROOT_DIR / "static"),
        static_url_path="/static",
    )
    app.config["DATABASE_URL"] = config.SQLALCHEMY_DATABASE_URI

    @app.get("/api/health")
    def health() -> Any:
        return {"status": "ok"}

    @app.get("/api/categories")
    def get_categories() -> Any:
        with session_scope() as session:
            stmt: Select[Category] = select(Category).options(joinedload(Category.products)).order_by(Category.name)
            categories = session.scalars(stmt).all()
            return jsonify([category.to_dict() for category in categories])

    @app.get("/api/products")
    def list_products() -> Any:
        category_slug = request.args.get("category")
        search_term = request.args.get("search")

        with session_scope() as session:
            stmt: Select[Product] = select(Product).options(joinedload(Product.category))

            if category_slug:
                stmt = stmt.join(Product.category).where(func.lower(Category.slug) == category_slug.lower())

            if search_term:
                stmt = stmt.where(func.lower(Product.name).like(f"%{search_term.lower()}%"))

            products = session.scalars(stmt.order_by(Product.name)).all()
            return jsonify([product.to_dict() for product in products])

    @app.get("/api/products/<int:product_id>")
    def product_detail(product_id: int) -> Any:
        with session_scope() as session:
            stmt = select(Product).options(joinedload(Product.category)).where(Product.id == product_id)
            product = session.scalars(stmt).first()
            if not product:
                abort(404, description="Product not found")
            return jsonify(product.to_dict())

    @app.post("/api/orders")
    def create_order() -> Any:
        payload = request.get_json(silent=True)
        if not payload:
            abort(400, description="JSON body is required")

        customer = payload.get("customer") or {}
        items = payload.get("items") or []

        name = (customer.get("name") or "").strip()
        email = (customer.get("email") or "").strip()
        address_parts = [
            customer.get("address1"),
            customer.get("address2"),
            customer.get("city"),
            customer.get("state"),
            customer.get("postal_code"),
            customer.get("country"),
        ]
        shipping_address = ", ".join(part for part in address_parts if part)

        if not name or not email or not shipping_address:
            abort(400, description="Customer name, email, and address are required")

        if not items:
            abort(400, description="At least one line item is required")

        product_map: dict[int, Product] = {}
        product_ids = [item.get("product_id") for item in items]
        if None in product_ids:
            abort(400, description="Each line item must include product_id")

        with session_scope() as session:
            stmt = select(Product).where(Product.id.in_(product_ids))
            for product in session.scalars(stmt):
                product_map[product.id] = product

            missing_ids = sorted(set(product_ids) - set(product_map.keys()))
            if missing_ids:
                abort(400, description=f"Unknown product ids: {missing_ids}")

            order = Order(
                customer_name=name,
                customer_email=email,
                shipping_address=shipping_address,
            )
            session.add(order)
            session.flush()

            order_items: list[OrderItem] = []
            for line in items:
                product_id = line["product_id"]
                quantity = int(line.get("quantity") or 0)
                if quantity <= 0:
                    abort(400, description="Quantity must be greater than zero")
                product = product_map[product_id]
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.price,
                )
                session.add(order_item)
                order_items.append(order_item)

            session.flush()

            total = sum(item.quantity * item.unit_price for item in order_items)

            response = {
                "order_id": order.id,
                "status": order.status,
                "total": total,
                "items": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                    }
                    for item in order_items
                ],
            }
            return jsonify(response), 201

    @app.get("/api/orders/<int:order_id>")
    def get_order(order_id: int) -> Any:
        with session_scope() as session:
            stmt = (
                select(Order)
                .options(joinedload(Order.items).joinedload(OrderItem.product))
                .where(Order.id == order_id)
            )
            order = session.scalars(stmt).first()
            if not order:
                abort(404, description="Order not found")
            return jsonify(order.to_dict())

    @app.get("/")
    def landing_page():
        return redirect(url_for("serve_page", page_name="home"))

    @app.get("/pages/<page_name>")
    def serve_page(page_name: str):
        page_key = page_name.lower()
        filename = config.FRONTEND_PAGES.get(page_key)
        if not filename:
            abort(404)
        return send_from_directory(config.ROOT_DIR, filename)

    return app


app = create_app()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    app.run(debug=True)
