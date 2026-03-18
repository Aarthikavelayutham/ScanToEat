import os
from django.core.management.base import BaseCommand
from django.conf import settings
from tables.models import Table

class Command(BaseCommand):
    help = 'Regenerate missing QR code images'

    def handle(self, *args, **options):
        self.stdout.write('Forcing regeneration of all QR codes to ensure correct SITE_URL...')
        tables = Table.objects.all()
        count = 0
        for table in tables:
            # Clear the old image to force our model's save() to regenerate it
            table.qr_image = None
            table.save()
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully regenerated {count} QR codes with the latest SITE_URL.'))
