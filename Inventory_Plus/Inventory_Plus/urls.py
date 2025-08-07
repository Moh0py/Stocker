# Inventory_Plus/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('inventory:dashboard')
    return redirect('accounts:login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_redirect, name='root'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('inventory/', include('inventory.urls', namespace='inventory')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)