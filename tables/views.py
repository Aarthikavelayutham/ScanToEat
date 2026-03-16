from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .models import Table
from orders.models import Order

@staff_member_required
def waiter_dashboard(request):
    active_tables = Table.objects.filter(is_active=True)
    table_data = []

    for table in active_tables:
        active_orders = Order.objects.filter(
            table=table,
            status__in=['pending', 'preparing', 'ready']
        ).prefetch_related('items__menu_item')

        total_amount = sum(o.total_amount for o in active_orders)

        table_data.append({
            'table': table,
            'orders': active_orders,
            'total_amount': total_amount,
            'has_ready': any(o.status == 'ready' for o in active_orders),
            'has_pending': any(o.status == 'pending' for o in active_orders),
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
            status__in=['pending', 'preparing', 'ready', 'delivered']
        )
        orders.update(status='billed')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


def qr_codes_page(request):
    tables = Table.objects.filter(is_active=True).order_by('number')
    return render(request, 'tables/qr_codes.html', {
        'tables': tables,
    })