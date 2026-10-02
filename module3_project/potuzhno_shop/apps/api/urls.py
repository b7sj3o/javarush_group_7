"""
Усі маршрути REST API v1 в одному місці.
Кожен feature-app (catalog, reviews, accounts, contact) дає свої view,
а тут вони збираються під /api/v1/.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import (
    MeView,
    RegisterView,
    ThrottledTokenObtainPairView,
    ThrottledTokenRefreshView,
)
from apps.catalog.views import (
    BrandViewSet,
    CategoryViewSet,
    ProductViewSet,
    SizeViewSet,
)
from apps.contact.views import ContactView
from apps.reviews.views import ProductReviewListView, ReviewViewSet

app_name = "api"

router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("categories", CategoryViewSet, basename="category")
router.register("brands", BrandViewSet, basename="brand")
router.register("sizes", SizeViewSet, basename="size")
router.register("reviews", ReviewViewSet, basename="review")

urlpatterns = [
    path("", include(router.urls)),

    path("products/<slug:slug>/reviews/", ProductReviewListView.as_view(), name="product-reviews"),

    path("token/", ThrottledTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", ThrottledTokenRefreshView.as_view(), name="token_refresh"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("users/me/", MeView.as_view(), name="users_me"),

    path("contact/", ContactView.as_view(), name="contact"),
]
