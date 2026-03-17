from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Prefetch
from .models import Table
from orders.models import Order

@staff_member_required
def waiter_dashboard(request):
    active_orders_qs = Order.objects.filter(
        status__in=['pending', 'preparing', 'ready']
    ).prefetch_related('items__menu_item')

    active_tables = Table.objects.filter(
        is_active=True
    ).prefetch_related(
        Prefetch('orders', queryset=active_orders_qs, to_attr='active_orders')
    ).order_by('number')

    table_data = []
    for table in active_tables:
        orders = table.active_orders
        total_amount = sum(o.total_amount for o in orders)

        table_data.append({
            'table': table,
            'orders': orders,
            'total_amount': total_amount,
            'has_ready': any(o.status == 'ready' for o in orders),
            'has_pending': any(o.status == 'pending' for o in orders),
        })

    return render(request, 'tables/waiter.html', {
        'table_data': table_data,
    })


@staff_member_required
def bill_table(request, table_id):
    if request.method == 'POST':
        table = get_object_or_404(Table, id=table_id)
        orders = Order.objects.filter(
            table=table,
            status__in=['ready', 'delivered']
        )
        orders.update(status='billed')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@staff_member_required
def qr_codes_page(request):
    tables = Table.objects.filter(is_active=True).order_by('number')
    return render(request, 'tables/qr_codes.html', {
        'tables': tables,
    })


@staff_member_required
def waiter_fragment(request):
    active_orders_qs = Order.objects.filter(
        status__in=['pending', 'preparing', 'ready']
    ).prefetch_related('items__menu_item')

    active_tables = Table.objects.filter(
        is_active=True
    ).prefetch_related(
        Prefetch('orders', queryset=active_orders_qs, to_attr='active_orders')
    ).order_by('number')

    table_data = []
    for table in active_tables:
        orders = table.active_orders
        total_amount = sum(o.total_amount for o in orders)

        table_data.append({
            'table': table,
            'orders': orders,
            'total_amount': total_amount,
            'has_ready': any(o.status == 'ready' for o in orders),
            'has_pending': any(o.status == 'pending' for o in orders),
        })

    return render(request, 'tables/waiter_fragment.html', {
        'table_data': table_data,
    })