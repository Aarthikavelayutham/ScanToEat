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
    
    # Session-based history
    history = request.session.get('chat_history', [])
    history.append({'role': 'user', 'content': message})
    
    all_items = MenuItem.objects.filter(is_available=True)
    all_cats = Category.objects.filter(is_active=True)
    
    # 1. Advanced Intent Recognition
    patterns = {
        'vegan': ['vegan', 'no dairy', 'no meat', 'plant based', 'pure veg'],
        'gluten': ['gluten-free', 'no wheat', 'celiac', 'flourless'],
        'time': ['time', 'open', 'close', 'hours', 'working', 'schedule'],
        'loc': ['location', 'where', 'place', 'address', 'directions'],
        'pay': ['pay', 'bill', 'payment', 'cash', 'card', 'upi', 'checkout'],
        'order': ['how to order', 'place order', 'add to cart', 'ordering process'],
        'chef_special': ['signature', 'best', 'famous', 'most popular', 'must try']
    }

    intent = next((k for k, v in patterns.items() if any(word in message for word in v)), None)
    
    items = MenuItem.objects.none()
    reply = ""

    # 2. Conversational Logic for "Any Question"
    if intent == 'time':
        reply = "We are open from 11:00 AM to 11:00 PM every day! 🕚 You can visit us anytime for a great meal."
    elif intent == 'loc':
        reply = "ScanToEat is located in the heart of the city! 📍 You can find our exact Google Maps location at the bottom of our homepage."
    elif intent == 'pay':
        reply = "We accept all major UPI apps, Cards, and Cash. 💳 Once you're done eating, just click the 'Generate Bill' button in your cart or ask the waiter!"
    elif intent == 'order':
        reply = "It's easy! 🛍️ Just click the 'Add' button on any dish you like. When you're ready, go to the 'Cart' and click 'Place Order'. Simple and fast!"
    elif intent == 'vegan':
        reply = "We have some delicious plant-based options! 🌿 I've selected our best vegan-friendly dishes for you:"
        items = all_items.filter(Q(description__icontains='vegan') | Q(description__icontains='fresh') | Q(name__icontains='salad'))
    elif intent == 'gluten':
        reply = "Looking for gluten-free? 🌾 While our kitchen handles flour, these dishes are made without gluten-based ingredients:"
        items = all_items.filter(Q(description__icontains='gluten-free') | Q(name__icontains='rice') | Q(name__icontains='soup'))
    elif intent == 'chef_special':
        reply = "As the Chef, these are my personal pride! 👨‍🍳 Don't leave without trying these signature specials:"
        items = all_items.order_by('?')[:3]
    else:
        # 3. Dynamic search across entire menu
        query = Q()
        words = message.split()
        for word in words:
            if len(word) > 2:
                query |= Q(name__icontains=word) | Q(description__icontains=word) | Q(category__name__icontains=word)
        
        items = all_items.filter(query).distinct()
        
        if items.exists():
            reply = "I found exactly what you're looking for our menu! 🍽️ Here's the best of what we have:"
        elif len(message) < 10:
             reply = "Hello! I'm your AI Chef. 👨‍🍳 I can recommend food, answer questions about our restaurant, or help you find specific ingredients. What's on your mind?"
        else:
             reply = "That's an interesting question! 👨‍🍳 While I focus on our menu and kitchen, I recommend trying these best-sellers while you wait for your answer:"
             items = all_items.order_by('?')[:3]

    # Process and Send
    final_items = items[:6]
    data = []
    for item in final_items:
        data.append({
            'id': str(item.id),
            'name': item.name,
            'price': float(item.price),
            'image': item.image.url if item.image else None,
            'desc': (item.description[:55] + '...') if item.description and len(item.description) > 55 else item.description
        })

    # Memory update
    history.append({'role': 'assistant', 'content': reply})
    request.session['chat_history'] = history[-6:]
    request.session.modified = True

    return JsonResponse({'reply': reply, 'recommendations': data})