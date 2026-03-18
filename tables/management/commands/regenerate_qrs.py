import os
from django.core.management.base import BaseCommand
from django.conf import settings
from tables.models import Table

class Command(BaseCommand):
    help = 'Regenerate missing QR code images'

    def handle(self, *args, **options):
        self.stdout.write('Checking and regenerating QR images for all tables...')
        tables = Table.objects.filter(is_active=True)
        count = 0
        for table in tables:
            # Our Table model's save method now handles the regeneration logic
            # even if the path exists in DB but the file is missing from disk.
            table.save()
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully checked/regenerated {count} QR codes.'))
