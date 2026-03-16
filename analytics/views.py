from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from django.db.models.functions import TruncHour
from orders.models import Order, OrderItem

@staff_member_required
def analytics_dashboard(request):
    # Most ordered items
    top_items = OrderItem.objects.values(
        'menu_item__name'
    ).annotate(
        total_ordered=Sum('quantity')
    ).order_by('-total_ordered')[:10]

    # Orders by hour
    orders_by_hour = Order.objects.annotate(
        hour=TruncHour('created_at')
    ).values('hour').annotate(
        count=Count('id')
    ).order_by('hour')[:24]

    # Summary stats
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    pending_orders = Order.objects.filter(status='pending').count()
    preparing_orders = Order.objects.filter(status='preparing').count()

    return render(request, 'analytics/dashboard.html', {
        'top_items': top_items,
        'orders_by_hour': orders_by_hour,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'preparing_orders': preparing_orders,
    })