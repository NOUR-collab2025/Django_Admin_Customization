from django.contrib import admin
from django.urls import path, include
from products.views import get_produit_prix
from products.admin import dashboard_view  # Assure-toi d'importer dashboard_view

urlpatterns = [
    path('get-produit-prix/<int:pk>/', get_produit_prix, name='get-produit-prix'),

    # Dashboard
    # Dashboard personnalisé
path('admin/dashboard/', admin.site.admin_view(dashboard_view), name='dashboard'),

# Admin officiel
path('admin/', admin.site.urls),

]

from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)