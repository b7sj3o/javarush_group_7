from django.conf import settings
from django.db import models


class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    # Рядком "catalog.Product", а не імпортом — так між app-ами не буде циклічних імпортів
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    rating = models.PositiveIntegerField(default=1, choices=RATING_CHOICES)
    text = models.TextField(blank=True, max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} -> {self.product} - {self.rating}"
