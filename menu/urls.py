from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_view, name='menu'),
    path('ai-recommendations/', views.ai_recommendations, name='ai_recommendations'),
]