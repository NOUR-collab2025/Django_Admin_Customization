from django.urls import path, include
from products.views import get_produit_prix
from products.admin import admin_site, dashboard_view  # Assure-toi d'importer dashboard_view

urlpatterns = [
    # API ou vues publiques
    path('get-produit-prix/<int:pk>/', get_produit_prix, name='get-produit-prix'),
    
    # Dashboard personnalisé
    path('admin/dashboard/', admin_site.admin_view(dashboard_view), name='dashboard'),
    
    # Admin classique avec ton CustomAdminSite
    path('admin/', admin_site.urls),
]
from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)