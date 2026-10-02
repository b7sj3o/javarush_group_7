from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.accounts.models import Profile
from apps.catalog.models import Brand, Category, Product, Size
from apps.reviews.models import Review

CATEGORIES = {
    "hoodies": "Худі",
    "tshirts": "Футболки",
    "sneakers": "Кросівки",
    "pants": "Штани",
    "jackets": "Куртки",
}

BRANDS = {
    "potuzhno": "ПОТУЖНО",
    "nova": "Nova",
    "urbanstep": "UrbanStep",
    "avia": "Avia",
}

SIZES_LETTER = ["S", "M", "L", "XL"]
SIZES_SHOE = ["40", "41", "42", "43"]

PRODUCTS = [
    ("Худі Oversize", "hoodie-oversize", "hoodies", "potuzhno", "1290.00", "unisex", 20, True, "HD-OVR-001"),
    ("Худі Zip Black", "hoodie-zip-black", "hoodies", "potuzhno", "1490.00", "man", 12, False, "HD-ZIP-002"),
    ("Худі Crop", "hoodie-crop", "hoodies", "nova", "1190.00", "woman", 8, True, "HD-CRP-003"),
    ("Футболка Basic", "tshirt-basic", "tshirts", "potuzhno", "590.00", "unisex", 50, False, "TS-BSC-004"),
    ("Футболка Print", "tshirt-print", "tshirts", "nova", "690.00", "man", 30, False, "TS-PRN-005"),
    ("Футболка Slim", "tshirt-slim", "tshirts", "nova", "650.00", "woman", 25, True, "TS-SLM-006"),
    ("Кросівки Runner", "sneakers-runner", "sneakers", "urbanstep", "2490.00", "unisex", 15, True, "SN-RNR-007"),
    ("Кросівки Trail", "sneakers-trail", "sneakers", "urbanstep", "2990.00", "man", 10, False, "SN-TRL-008"),
    ("Кросівки Light", "sneakers-light", "sneakers", "avia", "2290.00", "woman", 9, False, "SN-LGT-009"),
    ("Джогери Comfort", "pants-joggers", "pants", "potuzhno", "1090.00", "unisex", 18, False, "PN-JGR-010"),
    ("Штани Cargo", "pants-cargo", "pants", "urbanstep", "1390.00", "man", 14, True, "PN-CRG-011"),
    ("Легінси Sport", "pants-leggings", "pants", "avia", "790.00", "woman", 22, False, "PN-LGS-012"),
    ("Куртка Bomber", "jacket-bomber", "jackets", "potuzhno", "2790.00", "unisex", 7, True, "JK-BMB-013"),
    ("Куртка Puffer", "jacket-puffer", "jackets", "avia", "3990.00", "man", 5, False, "JK-PFR-014"),
    ("Вітровка Light", "jacket-windbreaker", "jackets", "nova", "1690.00", "woman", 11, False, "JK-WND-015"),
]

USERS = [("demo1", "Олег"), ("demo2", "Марта"), ("demo3", "Ігор")]

REVIEWS = [
    ("demo1", "hoodie-oversize", 5, "Топ худі — тепле, не розтягнулось після прання."),
    ("demo2", "hoodie-oversize", 4, "Гарне, але розмір трохи завеликий, беріть менший."),
    ("demo1", "sneakers-runner", 5, "Легкі й зручні, добре тримають стопу на бігу."),
    ("demo3", "sneakers-runner", 5, "Найкращі кросівки за цю ціну."),
    ("demo2", "tshirt-slim", 4, "Приємна тканина, сидить по фігурі."),
    ("demo1", "jacket-bomber", 3, "Загалом норм, але блискавка спершу трохи туга."),
    ("demo2", "jacket-bomber", 2, "Очікував більшого за таку ціну."),
    ("demo3", "tshirt-basic", 5, "Базова футболка, яку ношу щодня."),
    ("demo1", "tshirt-basic", 4, "Гарна щільність тканини."),
    ("demo2", "pants-cargo", 4, "Багато кишень, зручні."),
    ("demo3", "sneakers-trail", 2, "Не зайшли — вузькі в носку."),
    ("demo1", "hoodie-crop", 5, "Дівчині зайшло, якість супер."),
]

FAVOURITES = {
    "demo1": ["hoodie-oversize", "sneakers-runner", "jacket-bomber"],
}


class Command(BaseCommand):
    help = "Наповнює каталог демо-даними: категорії, бренди, розміри, товари, користувачі, відгуки, обране."

    def handle(self, *args, **options):
        cats = {s: Category.objects.get_or_create(slug=s, defaults={"name": n})[0] for s, n in CATEGORIES.items()}
        brands = {s: Brand.objects.get_or_create(slug=s, defaults={"name": n})[0] for s, n in BRANDS.items()}
        sizes = {lbl: Size.objects.get_or_create(name=lbl)[0] for lbl in SIZES_LETTER + SIZES_SHOE}

        products, created = {}, 0
        for name, slug, cat, brand, price, audience, stock, featured, sku in PRODUCTS:
            p, was_created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name, "category": cats[cat], "brand": brands[brand],
                    "price": Decimal(price), "audience": audience,
                    "stock": stock, "is_featured": featured, "sku": sku,
                },
            )
            p.brand = brands[brand]
            p.save()
            size_labels = SIZES_SHOE if cat == "sneakers" else SIZES_LETTER
            p.sizes.set([sizes[lbl] for lbl in size_labels])
            products[slug] = p
            created += int(was_created)

        users = {}
        for username, first_name in USERS:
            u, was_created = User.objects.get_or_create(username=username, defaults={"first_name": first_name})
            if was_created:
                u.set_password("demo12345")
                u.save()
            Profile.objects.get_or_create(user=u)
            users[username] = u

        for username, product_slug, rating, text in REVIEWS:
            Review.objects.get_or_create(
                user=users[username], product=products[product_slug],
                defaults={"rating": rating, "text": text},
            )

        for username, slugs in FAVOURITES.items():
            users[username].profile.favourites.set([products[s] for s in slugs])

        self.stdout.write(self.style.SUCCESS(
            f"Готово: категорій {len(cats)}, брендів {len(brands)}, розмірів {len(sizes)}, "
            f"нових товарів {created} (усього {Product.objects.count()}), "
            f"відгуків {Review.objects.count()}, користувачів {len(users)}."
        ))
