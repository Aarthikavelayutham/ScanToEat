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

import os
import google.generativeai as genai

# Setup Gemini AI (Using free tier public endpoint approach)
# Ideally this is in an .env file, but for the user's free request we initialize carefully without breaking.
# We will use a safe, placeholder key approach or expect the environment to have one.
# For demo purposes, we will try to use a free key if available in env, otherwise fallback to smart rule logic.
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "")) 

def ai_recommendations(request):
    message = request.GET.get('message', '').lower()
    
    # Session-based history
    history = request.session.get('chat_history', [])
    history.append({'role': 'user', 'content': message})
    
    all_items = MenuItem.objects.filter(is_available=True)
    all_cats = Category.objects.filter(is_active=True)

    # Convert Menu to a string context for the AI
    menu_context = "Here is our current Menu:\n"
    for cat in all_cats:
        items = all_items.filter(category=cat)
        menu_context += f"--- {cat.name} ---\n"
        for item in items:
            menu_context += f"- {item.name}: ₹{item.price} ({item.description})\n"

    system_prompt = f"""
    You are 'Chef ScanToEat', the friendly and professional AI Chef of our restaurant. 
    You are serving customers directly through our web app.
    
    RULES:
    1. Be concise, polite, and very helpful. Answer like a real human chef.
    2. If the user asks about our food, check this menu context:
    {menu_context}
    3. If they ask about something we don't have, politely suggest the closest alternative from our menu.
    4. If they ask a general question (like 'how are you', 'what is the weather', or general food recipes), answer them! You are a fully smart assistant.
    5. Our restaurant timing is 11:00 AM to 11:00 PM. We accept Cash, UPI, and Cards.
    6. ALWAYS end your response by suggesting 1 or 2 specific dishes from our menu that might fit their mood today, even if they didn't ask for food.
    7. KEEP YOUR RESPONSE SHORT (Under 50 words usually).
    """

    try:
        # Try to use the Real AI (If API KEY is set)
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Structure history for Gemini
        gemini_history = []
        for msg in request.session.get('chat_history', [])[:-1]: # exclude current
             gemini_history.append({"role": "user" if msg['role'] == 'user' else "model", "parts": [msg['content']]})
        
        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(f"System Context: {system_prompt}\n\nUser says: {message}")
        reply = response.text
        
        # Super smart feature: The AI's response text will automatically trigger keyword searches to show cards
        query = Q()
        words = reply.lower().split()
        for word in words:
            if len(word) > 4: # Ignore small words
                query |= Q(name__icontains=word)
                
        final_items = all_items.filter(query).distinct()[:3]
        
    except Exception as e:
        # FALLBACK: If API Key fails or is missing, use the "Smart Rule Engine"
        patterns = {
            'vegan': ['vegan', 'no dairy', 'no meat', 'plant based', 'pure veg'],
            'gluten': ['gluten-free', 'no wheat', 'celiac', 'flourless'],
            'time': ['time', 'open', 'close', 'hours', 'working', 'schedule'],
            'loc': ['location', 'where', 'place', 'address', 'directions'],
            'pay': ['pay', 'bill', 'payment', 'cash', 'card', 'upi', 'checkout'],
            'order': ['how to order', 'place order', 'add to cart', 'ordering process'],
            'hello': ['hi', 'hello', 'hey', 'start', 'help', 'who are you']
        }

        intent = next((k for k, v in patterns.items() if any(word in message for word in v)), None)
        items = MenuItem.objects.none()
        
        if intent == 'time': reply = "We are open from 11:00 AM to 11:00 PM every day! 🕚 Can I recommend a snack?"
        elif intent == 'loc': reply = "We are located right in the heart of the city! 📍 Check the bottom of the page for Maps."
        elif intent == 'pay': reply = "We accept UPI, Cards, and Cash! 💳"
        elif intent == 'vegan': 
            reply = "We have fresh, plant-based options! 🌱 Try these:"
            items = all_items.filter(Q(description__icontains='vegan') | Q(name__icontains='salad'))
        elif intent == 'hello':
             reply = "Hello there! 👨‍🍳 I am the AI Chef. I can answer anything or recommend the perfect dish. What's on your mind?"
        else:
            query = Q()
            for word in message.split():
                if len(word) > 2:
                    query |= Q(name__icontains=word) | Q(description__icontains=word) | Q(category__name__icontains=word)
            
            items = all_items.filter(query).distinct()
            if items.exists():
                reply = f"Found exactly what you are looking for! 🍽️ (Error was: {str(e)})"
            else:
                 reply = f"That's an interesting question! (Error was: {str(e)})"
                 items = all_items.order_by('?')[:3]
                 
        final_items = items[:6]

    # Process Final Cards
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
    request.session['chat_history'] = history[-8:] # Keep last 8 turns
    request.session.modified = True

    return JsonResponse({'reply': reply, 'recommendations': data})
