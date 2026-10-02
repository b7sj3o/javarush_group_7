from django.db.models import Exists, OuterRef, Value
from django.db.models.deletion import ProtectedError
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import Profile
from apps.api.pagination import StandardPagination
from apps.api.permissions import IsCatalogManagerOrReadOnly

from .filters import ProductFilter
from .models import Brand, Category, Product, Size
from .serializers import (
    BrandSerializer,
    CategorySerializer,
    ProductReadSerializer,
    ProductWriteSerializer,
    SizeSerializer,
)


class ProductViewSet(viewsets.ModelViewSet):
    """
    Каталог товарів: CRUD + додаткові дії (featured, favourites).
    Читати можуть усі, змінювати — лише менеджер каталогу.
    """

    serializer_class = ProductReadSerializer
    permission_classes = (IsCatalogManagerOrReadOnly,)
    # SEO-дружні URL: /api/v1/products/<slug>/ замість /products/<id>/
    lookup_field = "slug"
    queryset = (
        Product.objects.with_rating()
        .select_related("category", "brand")  # уникаємо N+1
        .prefetch_related("sizes")
    )
    pagination_class = StandardPagination
    filterset_class = ProductFilter
    search_fields = [
        "name",  # icontains
        "description",
        "=category__name",  # iexact
        "^brand__name",  # Adidas -> Adi
    ]
    ordering = ["-created_at", "-price"]
    ordering_fields = ["created_at", "price", "name", "is_active", "avg_rating"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.is_authenticated:
            return qs.annotate(is_favourite=Exists(
                Profile.favourites.through.objects.filter(
                    product_id=OuterRef("pk"), profile__user=user
                )
            ))

        return qs.annotate(is_favourite=Value(False))

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ProductWriteSerializer
        return ProductReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.save()
        response = ProductReadSerializer(product, context=self.get_serializer_context())
        return Response(response.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        product = serializer.save()
        response = ProductReadSerializer(product, context=self.get_serializer_context())
        return Response(response.data)

    @extend_schema(
        summary="Рекомендовані товари",
        description="Повертає товари з is_featured=True",
        responses={200: ProductReadSerializer(many=True)},
    )
    @action(detail=False, methods=["get"])
    def featured(self, request):
        products = self.filter_queryset(self.get_queryset()).filter(is_featured=True)

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    # Обране зберігається в accounts.Profile.favourites, але ендпоінти
    # живуть тут, бо це дії над товаром: POST/DELETE /products/<slug>/favourite/
    @extend_schema(
        summary="Додати товар в обране",
        request=None,
        responses={
            200: OpenApiResponse(description="Товар вже доданий до обраного"),
            201: OpenApiResponse(description="Товар додано в обране"),
            401: OpenApiResponse(description="Потрібна автентифікація"),
        },
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def favourite(self, request, slug=None):
        product = self.get_object()

        if request.user.profile.favourites.filter(pk=product.pk).exists():
            return Response({"detail": "Product already added to your favourites"}, status=status.HTTP_200_OK)

        request.user.profile.favourites.add(product)
        return Response({"detail": "Product was added to your favourites"}, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Видалити товар з обраного", request=None)
    @favourite.mapping.delete
    def remove_favourite(self, request, slug=None):
        product = self.get_object()
        request.user.profile.favourites.remove(product)

        return Response(status=status.HTTP_204_NO_CONTENT)

    # GET /products/favourites/ — обране поточного користувача (для сторінки профілю)
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def favourites(self, request):
        products = self.filter_queryset(self.get_queryset()).filter(
            favourited_by__user=request.user
        )

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class ProtectedDeleteMixin:
    """
    Category/Brand звʼязані з Product через on_delete=PROTECT: видалення запису,
    на який посилаються товари, кидає ProtectedError. Без цього міксина DRF
    відповів би 500 — перетворюємо на зрозумілий 409 Conflict.
    """

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "Неможливо видалити: на цей запис посилаються товари."},
                status=status.HTTP_409_CONFLICT,
            )


class CategoryViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = (IsCatalogManagerOrReadOnly,)
    queryset = Category.objects.all()
    pagination_class = StandardPagination


class BrandViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    serializer_class = BrandSerializer
    permission_classes = (IsCatalogManagerOrReadOnly,)
    queryset = Brand.objects.all()
    pagination_class = StandardPagination


class SizeViewSet(viewsets.ReadOnlyModelViewSet):
    """Довідник розмірів — потрібен формі товару в React (чекбокси розмірів)."""

    serializer_class = SizeSerializer
    queryset = Size.objects.order_by("id")
    pagination_class = None  # розмірів мало — пагінація лише заважає
