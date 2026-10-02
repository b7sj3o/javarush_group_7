from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.api.pagination import StandardPagination
from apps.api.permissions import IsReviewsModeratorOrReadOnly
from apps.catalog.models import Product

from .models import Review
from .serializers import ReviewReadSerializer, ReviewWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    /reviews/ — CRUD відгуків. Редагувати/видаляти може автор або модератор відгуків.
    """

    queryset = Review.objects.select_related("user", "product")
    permission_classes = (IsReviewsModeratorOrReadOnly,)
    pagination_class = StandardPagination

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ReviewReadSerializer
        return ReviewWriteSerializer

    # GET /reviews/mine/ — відгуки поточного користувача (сторінка профілю)
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def mine(self, request):
        reviews = (
            self.get_queryset()
            .filter(user=request.user)
            .order_by("-created_at")
        )

        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)


class ProductReviewListView(generics.ListAPIView):
    """GET /products/<slug>/reviews/ — відгуки конкретного товару (картка товару)."""

    queryset = Review.objects.select_related("user", "product")
    serializer_class = ReviewReadSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        product = get_object_or_404(Product, slug=self.kwargs["slug"])
        return super().get_queryset().filter(product=product).order_by("-created_at")
