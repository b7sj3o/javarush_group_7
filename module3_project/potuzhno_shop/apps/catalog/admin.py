from django.contrib import admin, messages
from django.db.models import Avg, Count

from .models import Brand, Category, Product, Size


@admin.action(description="Позначити рекомендованим")
def make_featured(modeladmin, request, queryset):
    updated = queryset.update(is_featured=True)
    modeladmin.message_user(request, f"{updated} товар(ів) позначено рекомендованими.", messages.SUCCESS)


@admin.action(description="Зняти позначку «рекомендований»")
def unmake_featured(modeladmin, request, queryset):
    updated = queryset.update(is_featured=False)
    modeladmin.message_user(request, f"{updated} товар(ів) знято з рекомендованих.", messages.WARNING)


@admin.action(description="Активувати (показувати в каталозі)")
def activate(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"{updated} товар(ів) активовано.", messages.SUCCESS)


@admin.action(description="Деактивувати (сховати з каталогу)")
def deactivate(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"{updated} товар(ів) деактивовано.", messages.WARNING)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name", "brand", "category", "price", "stock",
        "is_active", "is_featured",
        "avg_rating", "reviews_count",
    )
    list_display_links = ("name",)
    list_filter = ("category", "brand", "audience", "is_active", "is_featured")
    search_fields = ("name", "sku", "brand__name")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    actions = [make_featured, unmake_featured, activate, deactivate]

    fieldsets = (
        ("Основне", {"fields": ("name", "slug", "brand", "category", "audience")}),
        ("Ціна та склад", {"fields": ("price", "stock", "sku", "is_active", "is_featured")}),
        ("Розміри та опис", {"fields": ("sizes", "description"), "classes": ("collapse",)}),
        ("Службове", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _avg_rating=Avg("reviews__rating"),
            _reviews_count=Count("reviews", distinct=True),
        )

    @admin.display(description="Рейтинг", ordering="_avg_rating")
    def avg_rating(self, obj):
        return obj._avg_rating

    @admin.display(description="Відгуків", ordering="_reviews_count")
    def reviews_count(self, obj):
        return obj._reviews_count


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
