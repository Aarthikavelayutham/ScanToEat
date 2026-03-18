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
    message = request.GET.get('message', '').lower()
    
    # Initialize or get chat history from session
    history = request.session.get('chat_history', [])
    history.append({'role': 'user', 'content': message})
    
    # Intelligence: Category & Keyword Detection
    all_cats = Category.objects.filter(is_active=True)
    all_items = MenuItem.objects.filter(is_available=True)
    
    detected_cat = next((c for c in all_cats if c.name.lower() in message or c.slug.lower() in message), None)
    
    mood_map = {
        'spicy': ['spicy', 'chili', 'hot', 'masala', 'kick', 'fire', 'pepper'],
        'healthy': ['healthy', 'diet', 'green', 'fresh', 'oil-free', 'boiled', 'protein', 'salad'],
        'kids': ['kids', 'child', 'sweet', 'soft', 'non-spicy', 'plain', 'mini', 'small'],
        'chef': ['best', 'signature', 'special', 'must-try', 'chef', 'recommend', 'famous'],
        'drinks': ['drink', 'cold', 'beverage', 'juice', 'soda', 'refreshing']
    }
    
    current_intent = next((m for m, keywords in mood_map.items() if any(kw in message for kw in keywords)), None)
    
    # Reasoning logic for "Chat-GPT" feel
    if 'hi' in message or 'hello' in message or 'chef' in message:
        reply = "Hello! I'm Chef ScanToEat. 👨‍Chef at your service. I can help you find anything from a light snack to a grand feast! What's your appetite like today?"
        items = []
    elif detected_cat:
        reply = f"Ah, looking for {detected_cat.name}? Great choice! I've curated our entire selection of {detected_cat.name} just for you. Here they are:"
        items = all_items.filter(category=detected_cat)
    elif current_intent == 'spicy':
        reply = "I see you like some heat! 🌶️ I've picked out our boldest, most flavorful spicy dishes that will definitely give you that kick you're looking for:"
        items = all_items.filter(Q(name__icontains='spicy') | Q(name__icontains='chili') | Q(description__icontains='masala'))
    elif current_intent == 'healthy':
        reply = "Wise choice! 🥗 Health is wealth. These dishes are prepared with the freshest ingredients and minimal oil to keep you feeling light and energized:"
        items = all_items.filter(Q(description__icontains='healthy') | Q(category__name__icontains='Salad'))
    elif current_intent == 'kids':
        reply = "Cooking for the little ones? 🧸 I recommend these mild and fun dishes that are always a hit with kids:"
        items = all_items.filter(price__lt=200)[:4] # Simple logic for kids: affordable/small
    else:
        # Complex Search
        query = Q()
        words = message.split()
        for word in words:
            if len(word) > 3:
                query |= Q(name__icontains=word) | Q(description__icontains=word)
        
        items = all_items.filter(query)
        if items.exists():
            reply = "I've scanned our kitchen for items matching your request! Based on my recipes, these seem like the perfect match:"
        else:
            reply = "I'm not exactly sure about that, but as a Chef, I highly recommend you try our signature specials today! ✨"
            items = all_items.order_by('?')[:3]

    # Limit to 6 items for better chat readability
    items = items.distinct()[:6]
    
    data = []
    for item in items:
        data.append({
            'id': str(item.id),
            'name': item.name,
            'price': float(item.price),
            'image': item.image.url if item.image else None,
            'desc': (item.description[:50] + '...') if item.description and len(item.description) > 50 else item.description
        })

    # Save limited history back to session
    history.append({'role': 'assistant', 'content': reply})
    request.session['chat_history'] = history[-6:]
    request.session.modified = True

    return JsonResponse({
        'reply': reply,
        'recommendations': data
    })


