from products.admin import admin_site
from products.views import get_produit_prix

urlpatterns = [

    # API pour récupérer le prix d'un produit
    path('get-produit-prix/<int:pk>/', get_produit_prix, name='get-produit-prix'),

]