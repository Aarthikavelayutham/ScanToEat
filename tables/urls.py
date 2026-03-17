from django.urls import path
from . import views

urlpatterns = [
    path('waiter/', views.waiter_dashboard, name='waiter'),
    path('waiter/fragment/', views.waiter_fragment, name='waiter_fragment'),
    path('bill/<uuid:table_id>/', views.bill_table, name='bill_table'),
    path('qrcodes/', views.qr_codes_page, name='qr_codes'),
]