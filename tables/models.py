from django.db import models
from django.conf import settings
import uuid
import qrcode
from io import BytesIO
from django.core.files import File

class Table(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.PositiveIntegerField(unique=True)
    qr_token = models.UUIDField(default=uuid.uuid4, unique=True)
    qr_image = models.ImageField(upload_to='qrcodes/', blank=True)
    capacity = models.PositiveIntegerField(default=4)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.qr_image:
            url = f"{settings.SITE_URL}/menu/?table={self.qr_token}"
            qr = qrcode.make(url)
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