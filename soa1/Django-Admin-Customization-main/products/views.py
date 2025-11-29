from django.shortcuts import render
from .models import Produit
from django.http import JsonResponse
# Create your views here.
def get_produit_prix(request, pk):
    try:
        produit = Produit.objects.get(pk=pk)
        return JsonResponse({"prix": float(produit.prix)})
    except Produit.DoesNotExist:
        return JsonResponse({"prix": 0})
    
    
