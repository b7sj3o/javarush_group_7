from django.db import models
from django.db.models import Avg, Count
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)

    class Meta:
        ordering = ["name"]  # стабільний порядок для пагінації

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True).order_by("-created_at")

    def with_rating(self):
        # Відгуки живуть в apps.reviews; звертаємось через related_name="reviews"
        return self.annotate(
            avg_rating=Avg("reviews__rating"),
            reviews_count=Count("reviews", distinct=True),
        ).order_by("-created_at")


class Product(models.Model):
    AUDIENCE_CHOICES = [
        ("unisex", "Унісекс"),
        ("man", "Чоловіче"),
        ("woman", "Жіноче"),
    ]

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        null=False,
        related_name="products",
        related_query_name="product",
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, verbose_name="Пропонований?")

    sku = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        null=True, blank=True,
        verbose_name="Артикул",
        help_text="Унікальний код товару, напр. HD-OVR-001",
    )

    audience = models.CharField(
        max_length=10,
        choices=AUDIENCE_CHOICES,
        default="unisex",
        verbose_name="Аудиторія",
    )

    stock = models.PositiveIntegerField(default=0, verbose_name="Залишок")

    sizes = models.ManyToManyField(Size, blank=True)

    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


def unique_slug(name, instance=None):
    """
    Slug із назви товару, унікальний серед усіх Product.
    Якщо "hoodie" вже зайнятий — повертає "hoodie-2", "hoodie-3" і т.д.
    """
    base = slugify(name) or "product"

    queryset = Product.objects.all()
    if instance is not None and instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    slug, counter = base, 2
    while queryset.filter(slug=slug).exists():
        slug = f"{base}-{counter}"
        counter += 1
    return slug
