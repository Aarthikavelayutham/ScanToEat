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
    
    # Simple NLP: Pattern matching for conversational feel
    mood_map = {
        'spicy': ['spicy', 'chili', 'pepper', 'fire', 'hot', 'masala', 'schezwan', 'kick'],
        'healthy': ['healthy', 'diet', 'fresh', 'steam', 'green', 'boiled', 'leafy', 'salad', 'low calorie'],
        'light': ['light', 'soup', 'clear', 'simple', 'snack', 'starter', 'bite'],
        'filling': ['filling', 'hungry', 'meal', 'curry', 'rice', 'biryani', 'bread', 'roti', 'combo', 'main'],
        'sweet': ['sweet', 'dessert', 'ice cream', 'cake', 'sugar', 'chocolate', 'treat'],
        'popular': ['popular', 'best', 'signature', 'special', 'classic', 'recommend', 'suggest']
    }
    
    detected_mood = None
    for mood, keywords in mood_map.items():
        if any(kw in message for kw in keywords):
            detected_mood = mood
            break
            
    # Response Templates
    responses = {
        'spicy': "I love a good kick! 🌶️ Based on what you said, you'll definitely enjoy these spicy favorites:",
        'healthy': "Keeping it light and fresh? 🥗 Great choice! Here's what I recommend from our healthy selection:",
        'light': "Just looking for a quick bite? 🍃 These are perfect for starting your meal:",
        'filling': "Feeling hungry? 🍚 I've picked out our most satisfying and filling dishes for you:",
        'sweet': "Time for a treats? 🍰 Here are some delicious options to satisfy your sweet tooth:",
        'popular': "Since you're looking for our best, here are the top-rated dishes our customers love:",
        'default': "I'm not quite sure, but here are some of our most popular dishes that you might enjoy! ✨"
    }

    # Search Logic
    query = Q()
    if detected_mood:
        keywords = mood_map[detected_mood]
        for kw in keywords:
            query |= Q(name__icontains=kw) | Q(description__icontains=kw)
    
    items = MenuItem.objects.filter(is_available=True).filter(query)
    
    if not detected_mood or not items.exists():
        # Fallback to featured/random if no match or generic message
        all_ids = list(MenuItem.objects.filter(is_available=True).values_list('id', flat=True))
        if all_ids:
            random_ids = random.sample(all_ids, min(len(all_ids), 3))
            items = MenuItem.objects.filter(id__in=random_ids)
        else:
            items = MenuItem.objects.none()
        response_text = responses['default']
    else:
        items = items[:3]
        response_text = responses.get(detected_mood, responses['default'])


    # Greeting if message is generic
    greetings = ['hi', 'hello', 'hey', 'start', 'help', 'who are you']
    if any(g in message for g in greetings) and not detected_mood:
        response_text = "Hello! I'm your AI Chef. 👨‍🍳 I can help you find the perfect dish! Are you in the mood for something spicy, healthy, light, or perhaps a full meal?"
        items = [] # Just talk, don't show dishes yet

    data = []
    for item in items:
        data.append({
            'id': str(item.id),
            'name': item.name,
            'price': float(item.price),
            'image': item.image.url if item.image else None,
            'desc': (item.description[:45] + '...') if item.description and len(item.description) > 45 else item.description
        })
        
    return JsonResponse({
        'reply': response_text,
        'recommendations': data
    })
