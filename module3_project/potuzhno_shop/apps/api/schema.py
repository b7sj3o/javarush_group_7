"""
GraphQL-схема поверх тих самих моделей, що й REST API.
"""
import graphene
from django.contrib.auth.models import User
from django.db import transaction
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from apps.catalog.filters import ProductFilter
from apps.catalog.models import Brand, Category, Product
from apps.reviews.models import Review
from apps.reviews.serializers import ReviewWriteSerializer


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class BrandType(DjangoObjectType):
    class Meta:
        model = Brand
        fields = ("id", "name", "slug")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = (
            "id", "name", "slug", "description", "price", "category", "brand",
            "audience", "is_featured", "created_at",
        )


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("username", "first_name", "email")


class ReviewType(DjangoObjectType):
    class Meta:
        model = Review
        fields = ("id", "rating", "text", "user", "product")


class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (relay.Node,)  # обов'язково для Relay-пагінації
        fields = (
            "id", "name", "slug", "description", "price",
            "category", "brand", "audience", "is_featured", "created_at",
            "reviews",
        )

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.with_rating().select_related("category", "brand")


class Query(graphene.ObjectType):
    all_products = graphene.List(ProductType)
    product = graphene.Field(ProductType, slug=graphene.String(required=True))
    all_categories = graphene.List(CategoryType)
    all_reviews = graphene.List(ReviewType)
    products = DjangoFilterConnectionField(ProductNode, filterset_class=ProductFilter)

    def resolve_all_products(self, info):
        return (
            Product.objects.filter(is_active=True)
            .select_related("category", "brand")
            .prefetch_related("reviews__user", "sizes")
        )

    def resolve_product(self, info, slug):
        return Product.objects.get(slug=slug)

    def resolve_all_categories(self, info):
        return Category.objects.all()

    def resolve_all_reviews(self, info):
        return Review.objects.all()


class AddToFavourite(graphene.Mutation):
    class Arguments:
        slug = graphene.String(required=True)

    ok = graphene.Boolean()
    product = graphene.Field(ProductType)

    @staticmethod
    def mutate(root, info, slug):
        user = info.context.user

        if not user.is_authenticated:
            raise GraphQLError("Потрібно увійти в акаунт, щоб керувати улюбленими товарами")

        product = Product.objects.filter(slug=slug).first()
        if product is None:
            raise GraphQLError("Товар не знайдено")

        user.profile.favourites.add(product)

        return AddToFavourite(ok=True, product=product)


class RemoveFromFavourite(graphene.Mutation):
    class Arguments:
        slug = graphene.String(required=True)

    ok = graphene.Boolean()
    product = graphene.Field(ProductType)

    @staticmethod
    def mutate(root, info, slug):
        user = info.context.user

        if not user.is_authenticated:
            raise GraphQLError("Потрібно увійти в акаунт, щоб керувати улюбленими товарами")

        product = Product.objects.filter(slug=slug).first()
        if product is None:
            raise GraphQLError("Товар не знайдено")

        user.profile.favourites.remove(product)

        return RemoveFromFavourite(ok=True, product=product)


class AddReview(graphene.Mutation):
    class Arguments:
        product_slug = graphene.String(required=True)
        rating = graphene.Int(required=True)
        text = graphene.String()

    ok = graphene.Boolean()
    review = graphene.Field(ReviewType)
    errors = graphene.List(graphene.String)

    @staticmethod
    @transaction.atomic
    def mutate(root, info, product_slug, rating, text=""):
        user = info.context.user

        if not user.is_authenticated:
            raise GraphQLError("Потрібно увійти в акаунт, щоб створити відгук")

        product = Product.objects.filter(slug=product_slug).first()
        if product is None:
            raise GraphQLError("Продукту не існує")

        # Ті самі правила валідації, що й у REST: перевикористовуємо DRF-серіалізатор.
        # info.context — це Django request, з нього CurrentUserDefault бере user.
        serializer = ReviewWriteSerializer(
            data={"product": product.pk, "rating": rating, "text": text},
            context={"request": info.context},
        )

        if not serializer.is_valid():
            return AddReview(
                ok=False,
                errors=[str(msgs[0]) for field, msgs in serializer.errors.items()],
            )

        review = serializer.save()

        return AddReview(ok=True, review=review)


class Mutation(graphene.ObjectType):
    add_to_favourite = AddToFavourite.Field()
    remove_from_favourite = RemoveFromFavourite.Field()
    add_review = AddReview.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
