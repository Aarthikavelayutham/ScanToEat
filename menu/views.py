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
    
    # NLP improvement: Find specific categories mentioned in text
    all_categories = Category.objects.filter(is_active=True)
    detected_category = None
    for cat in all_categories:
        if cat.name.lower() in message or cat.slug.lower() in message:
            detected_category = cat
            break

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
        'spicy': "I love a good kick! 🌶️ Here are all the spicy dishes on our menu:",
        'healthy': "Keeping it light and fresh? 🥗 Here's our selection of healthy options:",
        'light': "Just looking for a quick bite? 🍃 Check these out:",
        'filling': "Feeling hungry? 🍚 These are our most satisfying and filling dishes:",
        'sweet': "Time for a treats? 🍰 Here are our sweet delights:",
        'popular': "Since you're looking for our best, check out these popular favorites:",
        'default': "I've picked out some of our best dishes that I think you'll enjoy! ✨"
    }

    # Search Logic
    query = Q()
    if detected_mood:
        keywords = mood_map[detected_mood]
        for kw in keywords:
            query |= Q(name__icontains=kw) | Q(description__icontains=kw)
    
    if detected_category:
        query |= Q(category=detected_category)
    
    items = MenuItem.objects.filter(is_available=True).filter(query).distinct()
    
    if not (detected_mood or detected_category) or not items.exists():
        # Fallback to featured/random if no match or generic message
        all_ids = list(MenuItem.objects.filter(is_available=True).values_list('id', flat=True))
        if all_ids:
            random_ids = random.sample(all_ids, min(len(all_ids), 3)) # Keep random as small
            items = MenuItem.objects.filter(id__in=random_ids)
        else:
            items = MenuItem.objects.none()
        response_text = responses['default']
    else:
        # DO NOT limit 3 anymore as per user request
        if detected_category:
            response_text = f"Sure! Here are all the dishes from our **{detected_category.name}** category: 🍽️"
        else:
            response_text = responses.get(detected_mood, responses['default'])

    # Greeting if message is generic
    greetings = ['hi', 'hello', 'hey', 'start', 'help', 'who are you']
    if any(g in message for g in greetings) and not (detected_mood or detected_category):
        response_text = "Hello! I'm your AI Chef. 👨‍🍳 I can help you find the perfect dish! Try asking for 'spicy food', 'all starters', or something 'healthy'!"
        items = [] # Just talk

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

