# import pytest
# from django.urls import reverse
# from rest_framework import status
#
# from apps.catalog.models import Brand, Category, Product
#
#
# def test_product_list_returns_200(api_client, product):
#     url = reverse("api:product-list")
#     response = api_client.get(url)
#
#     assert response.status_code == 200
#     assert response.data["pagination"]["count"] == 1
#     assert response.data["results"][0]["name"] == "Худі Oversize"
#
#
#
# def test_pagination_uses_page_number_param(api_client, category, brand):
#     for i in range(25):
#         Product.objects.create(
#             name=f"Товар {i}", slug=f"tovar-{i}", price="100.00",
#             category=category, brand=brand,
#         )
#
#     url = reverse("api:product-list")
#     response = api_client.get(url, {"page_number": 2})
#
#     assert response.data["pagination"]["current"] == 2
#
#
# @pytest.mark.django_db
# def test_create_product_as_manager(api_client, catalog_manager, category, brand):
#     api_client.force_authenticate(user=catalog_manager)
#     url = reverse("api:product-list")
#     payload = {
#         "name": "Нове худі",
#         "price": "999.00",
#         "stock": 5,
#         "audience": "unisex",
#         "category": category.id,
#         "brand": brand.id,
#     }
#
#     response = api_client.post(url, payload, format="json")
#
#     assert response.status_code == status.HTTP_201_CREATED
#     assert Product.objects.filter(name="Нове худі").exists()
#
#
# @pytest.mark.parametrize(
#     "payload, bad_field",
#     [
#         ({"name": "", "price": "100.00"}, "name"),
#         ({"name": "Товар", "price": "-100"}, "price"),
#         ({"name": "Товар", "price": "100.00", "category": 99999}, "category"),
#     ],
# )
# def test_create_product_invalid(
#     api_client, catalog_manager, category, brand, payload, bad_field
# ):
#     api_client.force_authenticate(user=catalog_manager)
#     payload.setdefault("category", category.id)
#     payload.setdefault("brand", brand.id)
#
#     response = api_client.post(reverse("api:product-list"), payload, format="json")
#
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert bad_field in response.data
#
#
# def test_update_product(api_client, catalog_manager, product):
#     api_client.force_authenticate(user=catalog_manager)
#     url = reverse("api:product-detail", args=[product.slug])
#
#
#     response = api_client.patch(url, {"price": "555.00"}, format="json")
#
#     assert response.status_code == status.HTTP_200_OK
#     product.refresh_from_db() # !!!
#     assert str(product.price) == "555.00"
#
#
# def test_delete_product(api_client, catalog_manager, product):
#     api_client.force_authenticate(user=catalog_manager)
#     url = reverse("api:product-detail", args=[product.slug])
#
#     response = api_client.delete(url)
#
#     assert response.status_code == status.HTTP_204_NO_CONTENT
#     assert not Product.objects.filter(pk=product.pk).exists()
#
#
#
# def test_anonymous_cannot_create(api_client, category, brand):
#     response = api_client.post(
#         reverse("api:product-list"),
#         {"name": "X", "price": "1.00", "category": category.id, "brand": brand.id},
#         format="json",
#     )
#
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
#
#
# def test_regular_user_cannot_create(api_client, user, category, brand):
#     api_client.force_authenticate(user=user)
#
#     response = api_client.post(
#         reverse("api:product-list"),
#         {"name": "X", "price": "1.00", "category": category.id, "brand": brand.id},
#         format="json",
#     )
#
#     assert response.status_code == status.HTTP_403_FORBIDDEN
#
#
# def test_catalog_manager_can_create(api_client, catalog_manager, category, brand):
#     api_client.force_authenticate(user=catalog_manager)
#
#     response = api_client.post(
#         reverse("api:product-list"),
#         {"name": "X", "price": "1.00", "category": category.id, "brand": brand.id},
#         format="json",
#     )
#
#     assert response.status_code == status.HTTP_201_CREATED
