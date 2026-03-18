import os
import uuid
import qrcode
from io import BytesIO
from django.db import models
from django.conf import settings
from django.core.files import File

class Table(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.PositiveIntegerField(unique=True)
    qr_token = models.UUIDField(default=uuid.uuid4, unique=True)
    qr_image = models.ImageField(upload_to='qrcodes/', blank=True)
    capacity = models.PositiveIntegerField(default=4)
    is_active = models.BooleanField(default=True)

    @property
    def qr_url(self):
        return f"{settings.SITE_URL}/menu/?table={self.qr_token}"

    def save(self, *args, **kwargs):
        # Check if qr_image exists in DB or if the physical file is missing
        must_generate = not self.qr_image
        if self.qr_image:
            try:
                if not os.path.exists(self.qr_image.path):
                    must_generate = True
            except (ValueError, AttributeError):
                must_generate = True

        if must_generate:
            qr = qrcode.make(self.qr_url)
            buffer = BytesIO()
            qr.save(buffer, format='PNG')
            self.qr_image.save(
                f'table_{self.number}.png',
                File(buffer),
                save=False
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Table {self.number}"