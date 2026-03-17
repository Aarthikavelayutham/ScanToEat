import os
import json
import django
from django.core import serializers

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scantoeat.settings')
django.setup()

from menu.models import Category, MenuItem
from tables.models import Table

def export_data(model_list, filename):
    print(f"Exporting {filename}...")
    data = serializers.serialize("json", model_list, indent=2)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(data)
    print(f"Successfully exported {filename}!")

if __name__ == "__main__":
    export_data(list(Category.objects.all()) + list(MenuItem.objects.all()), "menu_data.json")
    export_data(list(Table.objects.all()), "tables_data.json")
