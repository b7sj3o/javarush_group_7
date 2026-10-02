from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)

    # Обране: рядком "catalog.Product", щоб не імпортувати catalog з accounts
    favourites = models.ManyToManyField(
        "catalog.Product",
        related_name="favourited_by",
        blank=True,
    )

    def __str__(self):
        return self.user.username
