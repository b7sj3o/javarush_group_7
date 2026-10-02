from django_filters import rest_framework as filters

from .models import Brand, Category, Product, Size


class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    # /products?min_price=1000 -> price__gte = 1000
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")

    # Чекбокси в стилі Rozetka: параметр повторюється в URL
    # (?category=hudi&category=kurtky). Значення однієї групи об'єднуються
    # через OR (slug__in=[...]), різні групи — через AND (звичайний filter-ланцюг).
    category = filters.ModelMultipleChoiceFilter(
        field_name="category__slug",
        to_field_name="slug",
        queryset=Category.objects.all(),
    )
    brand = filters.ModelMultipleChoiceFilter(
        field_name="brand__slug",
        to_field_name="slug",
        queryset=Brand.objects.all(),
    )
    # M2M: товар з розмірами S і M при ?size=S&size=M потрапив би у видачу двічі,
    # тому distinct=True обов'язковий
    size = filters.ModelMultipleChoiceFilter(
        field_name="sizes__name",
        to_field_name="name",
        queryset=Size.objects.all(),
        distinct=True,
    )
    audience = filters.MultipleChoiceFilter(choices=Product.AUDIENCE_CHOICES)

    min_rating = filters.NumberFilter(field_name="avg_rating", lookup_expr="gte")
    in_stock = filters.BooleanFilter(method="filter_in_stock", label="Чи є в наявності")

    class Meta:
        model = Product
        fields = ["is_active", "is_featured"]

    def filter_in_stock(self, queryset, name, value):
        if value is True:
            return queryset.filter(stock__gt=0)
        if value is False:
            return queryset.filter(stock=0)
        return queryset
