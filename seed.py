from __future__ import annotations

from random import randint

from sqlalchemy import select

from .database import Base, engine, session_scope
from .models import Category, Order, OrderItem, Product

CATEGORIES = (
    "New Arrivals",
    "Dresses",
    "Tops",
    "Denim",
    "Essentials",
)

PRODUCTS = [
    {
        "name": "Classic Crewneck Tee",
        "price": 29.99,
        "description": "Soft cotton tee with a relaxed silhouette for everyday wear.",
        "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuDouwwcGryi6Ng2NOTr52ufBBUVhzWwv5GkDdeV_EH9__KQKTfiZjKA2r2AGY0JPaHujYXe6sxNZmDsWKOp47cUnaSAjuESC2hH1eLM3Pfu-tpO1on_SP5C51cQlAOCaEESEgL4Dmbk646lTB_uBT_OOOuzNWoirz-1UZvNNRSML5iYcpdAkVrXEYDYIWCBW9Scm9pofIxALJ1p6MCL3RlD0MTMItSCYTHvnu3tNLlm_j5H7jqwsFbGR9XQyA8SKiIwMsWmHE4d0u2p",
        "category": "Tops",
    },
    {
        "name": "Essential V-Neck",
        "price": 24.50,
        "description": "Lightweight v-neck that layers perfectly under blazers or cardigans.",
        "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuDRchNKvGweusLod13nxnNizmAM0CKVPIMljkaECqK2xA4GxlAJFcMfZnIH4V9ZzMfkkLZpDnDwyg7soGb-cijqUxP305Yc_zO1QG-bBkkIwRcC1GMGJfHg4W83te7-WBd4B2RzpOmDmmDaW0hyacmePGQwZ7eZyRLCg0pXiTlsvdlOZgAH6vqw0erROWZvl8Ytpej0lHsxMA3rG7o71JH1HBtka8QRCIg0e9t3Y40ABhdDoNsPwHzABZ5CQ1VA6hpV9969Kqgfsiw3",
        "category": "Tops",
    },
    {
        "name": "Striped Long Sleeve",
        "price": 35.00,
        "description": "Breton-inspired stripes on breathable organic cotton.",
        "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuBhiyIVMK6BcYKWPCRalf41PwD2gET3c2RwTPmpepRsSamZ5i0CH-mmpoFVohE_asCUxyhY-ofT9cBJ8cchj9EpuE47TUVzUF_kL9bIoLmlh-xQXElyO2yKm6kn4sYMZww6bK4d6NNl4O9T3_6b_GO6467r7iShCD0Nr07fMk9ppu3WiiKqGyKSlT6XTvwa5MPj9uwiamdPBvFgaP__R0qFPsGJ3Scivc2rT8htktrUTaKagVJiw3rVB4m5K2pKXOj3Yf0WcIEAIEvY",
        "category": "Dresses",
    },
    {
        "name": "Heather Grey Basic Tee",
        "price": 19.99,
        "description": "Premium jersey knit with a tailored unisex fit.",
        "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuBV-57Jc_tljg1V3GWq9_6_ThATY28MnLV0O5ELHEmyh10ofcMJhi3287Bv5KMfZUKASp1WGXtXhSKnKV5WfZ-lXQYPD64k0H2jBBijg0AshVlYSFsdUTGBk3mk0cgbkCqKaZuyRqEFNqbbO1RO6EQkLxSnQYCpzCcZGaMG1NrEFYYNKFRp0_RGM_7pOcsX_DQ1GxTV5wF8hqSYd2MqxOD3xEyaKHShjtn4gK74Jw9F8dfBxTJhUgqioVVRQfL6sunDV28HbhgWNia4",
        "category": "Essentials",
    },
    {
        "name": "Vintage Graphic Tee",
        "price": 42.00,
        "description": "Limited-edition artwork printed with water-based inks.",
        "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuDzjGJRgvwREQjSMQ66YFbnP1XVewQmhZOVveCdMVMEO9-gxkGcgitvnntNe40x2yz8Uh-OKcKc5roSYYtGQN7OoVDTWZQJPd9qQFj7VEfLOTvJe_yCFEno_Egjbvhwls4PuKS2Qk1iV19f0HqvQHaVdseyDhIO0T57HE0OWTCD4CYUW_E5B__IsDoAPWh8wg-yhjnJ2yeypPa4ANuVj87D89Dd1CpS8SCIp9iHaJr51nMq6Rv8yo8cbpv4S0t_xaEa5tEzyyh0k86C",
        "category": "New Arrivals",
    },
    {
        "name": "Slub Cotton Pocket Tee",
        "price": 32.99,
        "description": "Texture-rich cotton with a single utility pocket.",
        "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuBkVdj8BHwwxW1m5ahPAdm1yaRvswlGGarFDTx9sZsvGvMNEBdpJuz_33qUq64XLA6nQdxNM3UNW3upTeokt5Z_6vYAMgTDvzWZinSClLi9_uWIjPqCxoyTk25qkqEaMvkAl0En-Px4DrCovMFNfwfJh2MU3J5-xYGM0cADha9TpyjQX4yRgTXmIFTzvhDkkw7FYk_qZi7pn-o0htPnufzCb3IMDGSgUE_0WObt0PGHS22lOFzqIjTR2kK5EyGYaoVWnJVX7R_sy0PH",
        "category": "Essentials",
    },
]


def slugify(value: str) -> str:
    return value.lower().replace(" ", "-")


def seed() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with session_scope() as session:
        slug_map: dict[str, Category] = {}
        for name in CATEGORIES:
            category = Category(name=name, slug=slugify(name))
            session.add(category)
            slug_map[name] = category

        session.flush()

        product_objs = []
        for product in PRODUCTS:
            category = slug_map[product["category"]]
            product_obj = Product(
                name=product["name"],
                price=product["price"],
                description=product["description"],
                image_url=product["image_url"],
                category_id=category.id,
            )
            session.add(product_obj)
            product_objs.append(product_obj)

        session.flush()

        sample_order = Order(
            customer_name="Alex Morgan",
            customer_email="alex.morgan@example.com",
            shipping_address="123 Market Street, San Francisco, CA",
        )
        session.add(sample_order)
        session.flush()

        for product in product_objs[:3]:
            item = OrderItem(
                order_id=sample_order.id,
                product_id=product.id,
                quantity=randint(1, 3),
                unit_price=product.price,
            )
            session.add(item)

    print("Database seeded with demo data.")


if __name__ == "__main__":
    seed()
