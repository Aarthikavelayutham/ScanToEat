from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from orders.models import Order

@staff_member_required
def kitchen_dashboard(request):
    orders = Order.objects.filter(
        status__in=['pending', 'preparing']
    ).select_related('table').prefetch_related('items__menu_item')
    return render(request, 'kitchen/dashboard.html', {
        'orders': orders,
    })

@staff_member_required
def update_order_status(request, order_id):
    VALID_TRANSITIONS = {
        'pending': ['preparing'],
        'preparing': ['ready'],
        'ready': ['delivered'],
    }
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        allowed = VALID_TRANSITIONS.get(order.status, [])
        if new_status in allowed:
            order.status = new_status
            order.save()
            return JsonResponse({'success': True, 'status': order.status})
        return JsonResponse({'success': False, 'error': f'Cannot transition from {order.status} to {new_status}'})
    return JsonResponse({'success': False})

@staff_member_required
def kitchen_orders_fragment(request):
    orders = Order.objects.filter(
        status__in=['pending', 'preparing']
    ).select_related('table').prefetch_related('items__menu_item')
    return render(request, 'kitchen/orders_fragment.html', {
        'orders': orders,
    })