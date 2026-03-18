from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from .models import Category, MenuItem
from tables.models import Table
import random

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

def ai_recommendations(request):
    mood = request.GET.get('mood', '').lower()
    
    # AI logic: Keyword matching in name and description
    # Mapping moods/preferences to keywords
    mood_map = {
        'spicy': ['spicy', 'chili', 'pepper', 'fire', 'hot', 'masala', 'schezwan'],
        'healthy': ['healthy', 'salad', 'fresh', 'steam', 'green', 'boiled', 'leafy'],
        'light': ['light', 'soup', 'clear', 'simple', 'snack', 'starter'],
        'filling': ['filling', 'meal', 'curry', 'rice', 'biryani', 'bread', 'roti', 'combo'],
        'sweet': ['sweet', 'dessert', 'ice cream', 'cake', 'sugar', 'chocolate'],
        'popular': ['featured', 'chef', 'signature', 'special', 'classic']
    }
    
    keywords = mood_map.get(mood, [])
    
    # Build query
    query = Q()
    for kw in keywords:
        query |= Q(name__icontains=kw) | Q(description__icontains=kw)
        
    # If no results or unknown mood, pick random items
    items = MenuItem.objects.filter(is_available=True).filter(query)
    
    if not items.exists() or not keywords:
        # Pick 3 random items if no specific match
        all_ids = MenuItem.objects.filter(is_available=True).values_list('id', flat=True)
        random_ids = random.sample(list(all_ids), min(len(all_ids), 3))
        items = MenuItem.objects.filter(id__in=random_ids)
    else:
        # Limited to 3 results
        items = items[:3]
        
    data = []
    for item in items:
        data.append({
            'id': str(item.id),
            'name': item.name,
            'price': float(item.price),
            'image': item.image.url if item.image else None,
            'desc': (item.description[:45] + '...') if item.description and len(item.description) > 45 else item.description
        })
        
    return JsonResponse({'recommendations': data})