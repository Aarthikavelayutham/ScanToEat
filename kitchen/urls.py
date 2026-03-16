from django.urls import path
from . import views

urlpatterns = [
    path('', views.kitchen_dashboard, name='kitchen'),
    path('update/<uuid:order_id>/', views.update_order_status, name='update_order_status'),
    path('fragment/', views.kitchen_orders_fragment, name='kitchen_fragment'),
]