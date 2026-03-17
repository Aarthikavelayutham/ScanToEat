from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.shortcuts import render
from django.views.static import serve

def home(request):
    return render(request, 'home.html')

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('menu/', include('menu.urls')),
    path('orders/', include('orders.urls')),
    path('kitchen/', include('kitchen.urls')),
    path('analytics/', include('analytics.urls')),
    path('tables/', include('tables.urls')),
    # Force serve media files in production
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]