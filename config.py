from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
DATABASE_PATH = BASE_DIR / "app.db"
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"

FRONTEND_PAGES = {
    "home": "home.html",
    "products": "products.html",
    "product": "product.html",
    "cart": "cart.html",
    "order": "order.html",
    "shipping": "shippinginfo.html",
    "tryon": "tryon.html",
    "experience": "experience.html",
    "bmi": "bmi.html",
    "wishlist": "wishlist.html",
}
