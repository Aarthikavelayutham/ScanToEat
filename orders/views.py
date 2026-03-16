from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import transaction
from menu.models import MenuItem
from tables.models import Table
from .models import Order, OrderItem

def add_to_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        try:
            item = MenuItem.objects.get(id=item_id, is_available=True)
            cart = request.session.get('cart', {})
            if item_id in cart:
                cart[item_id]['quantity'] += 1
            else:
                cart[item_id] = {
                    'name': item.name,
                    'price': str(item.price),
                    'quantity': 1,
                }
            request.session['cart'] = cart
            request.session.modified = True
            total_items = sum(i['quantity'] for i in cart.values())
            return JsonResponse({'success': True, 'total_items': total_items})
        except MenuItem.DoesNotExist:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})


def cart_view(request):
    cart = request.session.get('cart', {})
    table_number = request.session.get('table_number')
    cart_items = []
    total = 0
    for item_id, item in cart.items():
        subtotal = float(item['price']) * item['quantity']
        total += subtotal
        cart_items.append({
            'id': item_id,
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'subtotal': subtotal,
        })
    return render(request, 'orders/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'table_number': table_number,
    })


def remove_from_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        cart = request.session.get('cart', {})
        if item_id in cart:
            del cart[item_id]
            request.session['cart'] = cart
            request.session.modified = True
    return redirect('cart')


def place_order(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        table_id = request.session.get('table_id')
        if not cart:
            return redirect('cart')
        if not table_id:
            return redirect('menu')
        try:
            table = Table.objects.get(id=table_id)
            with transaction.atomic():
                order = Order.objects.create(
                    table=table,
                    status='pending',
                    total_amount=sum(
                        float(i['price']) * i['quantity']
                        for i in cart.values()
                    )
                )
                for item_id, item in cart.items():
                    menu_item = MenuItem.objects.get(id=item_id)
                    OrderItem.objects.create(
                        order=order,
                        menu_item=menu_item,
                        quantity=item['quantity'],
                        unit_price=item['price'],
                    )
                del request.session['cart']
                request.session.modified = True
            return redirect('order_success')
        except Exception as e:
            return redirect('cart')
    return redirect('cart')


def order_success(request):
    return render(request, 'orders/order_success.html')
    