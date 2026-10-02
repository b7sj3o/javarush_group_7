from sqlalchemy.orm import Session

from .models import Category, Product


def seed_data(db: Session) -> None:
    if db.query(Product).first():
        return

    tech = Category(
        name="Tech",
        description="Gadgets for work, study, and everyday life.",
    )
    home = Category(
        name="Home",
        description="Simple items that make your home more comfortable.",
    )

    db.add_all([tech, home])
    db.flush()

    db.add_all(
        [
            Product(
                title="Aurora Wireless Headphones",
                short_description="Light headphones with clear sound and soft ear pads.",
                description=(
                    "Comfortable wireless headphones for music, calls, and studying. "
                    "The battery lasts up to 30 hours, and the foldable body fits easily "
                    "into a backpack."
                ),
                price=79.99,
                image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80",
                stock=24,
                category_id=tech.id,
            ),
            Product(
                title="Nimbus Desk Lamp",
                short_description="Minimal LED lamp with warm and cold light modes.",
                description=(
                    "A compact lamp for a focused workspace. Choose between three "
                    "brightness levels and adjust the angle for reading, coding, or sketching."
                ),
                price=34.50,
                image_url="https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=900&q=80",
                stock=38,
                category_id=home.id,
            ),
            Product(
                title="Terra Ceramic Mug",
                short_description="Handy ceramic mug for coffee, tea, or cocoa.",
                description=(
                    "A durable 350 ml mug with a matte finish. It keeps drinks warm "
                    "during long mornings and looks good on any desk."
                ),
                price=12.90,
                image_url="https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=80",
                stock=57,
                category_id=home.id,
            ),
            Product(
                title="Pulse Smart Watch",
                short_description="Everyday watch with activity tracking and notifications.",
                description=(
                    "Track steps, workouts, sleep, and messages from your phone. "
                    "The bright display is easy to read outside, and the strap is replaceable."
                ),
                price=129.00,
                image_url="https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80",
                stock=16,
                category_id=tech.id,
            ),
        ]
    )
    db.commit()
