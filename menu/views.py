from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
from .models import Category, MenuItem
from tables.models import Table

def menu_view(request):
    table_token = request.GET.get('table')
    table = None
    
    if table_token:
        try:
            table = Table.objects.get(qr_token=table_token, is_active=True)
            request.session['table_id'] = str(table.id)
            request.session['table_number'] = table.number
        except Table.DoesNotExist:
            pass

    categories = Category.objects.filter(
        is_active=True
    ).prefetch_related(
        Prefetch('items', queryset=MenuItem.objects.filter(is_available=True))
    )

    return render(request, 'menu/menu.html', {
        'categories': categories,
        'table': table,
    })