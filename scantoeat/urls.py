from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render


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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)