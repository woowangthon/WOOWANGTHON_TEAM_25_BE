from django.db import models


class ScanCache(models.Model):
    url = models.CharField(
        max_length=2048,
        unique=True
    )

    result = models.JSONField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )
