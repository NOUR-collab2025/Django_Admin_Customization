from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.utils.html import format_html, format_html_join
from django import forms
from ckeditor.widgets import CKEditorWidget
from django.contrib.admin import widgets
from django.shortcuts import render
from django.db import models
from django.db.models import Count 
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

from .models import Client, Produit, Categorie, Commande, ArticleCommande


# -----------------------------------------
# DASHBOARD VIEW
# -----------------------------------------

def dashboard_view(request):
    # Statistiques principales
    total_clients = Client.objects.count()
    total_commandes = Commande.objects.count()
    total_produits = Produit.objects.count()

    # Commandes par statut
    commandes_par_statut = Commande.objects.values('statut')\
        .annotate(count=Count('id')).order_by('statut')

    # Dernières commandes
    dernieres_commandes = Commande.objects.order_by('-cree_le')[:5]

    # Produits en faible stock
    produits_faible_stock = Produit.objects.filter(stock__lt=5)

    context = {
        'total_clients': total_clients,
        'total_commandes': total_commandes,
        'total_produits': total_produits,
        'commandes_par_statut': commandes_par_statut,
        'dernieres_commandes': dernieres_commandes,
        'produits_faible_stock': produits_faible_stock,
    }

    return render(request, 'admin/dashboard.html', context)


# -----------------------------------------
# Inline ArticleCommande
# -----------------------------------------

class ArticleCommandeInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if not any(form.cleaned_data and not form.cleaned_data.get('DELETE', False) for form in self.forms):
            raise ValidationError("Vous devez ajouter au moins un produit.")


class ArticleCommandeInline(admin.TabularInline):
    model = ArticleCommande
    extra = 1
    autocomplete_fields = ('produit',)
    formset = ArticleCommandeInlineFormSet


# -----------------------------------------
# Commande Admin
# -----------------------------------------

class CommandeAdminForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = '__all__'
        widgets = {
            'cree_le': widgets.AdminSplitDateTime(),
            'modifie_le': widgets.AdminSplitDateTime(),
        }


class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'statut', 'prix_total', 'cree_le', 'modifie_le', 'articles_affiches')
    search_fields = ('client__prenom', 'client__nom')
    list_filter = ('statut',)
    inlines = [ArticleCommandeInline]
    form = CommandeAdminForm

    class Media:
        js = ('js/commande_admin.js',)

    def articles_affiches(self, obj):
        articles = obj.articlecommande_set.all()
        if not articles:
            return "-"
        return format_html_join(
            "<br>",
            '<img src="{}" width="40" height="40"> {} x {} = {} DT',
            (
                (
                    a.produit.image.url if a.produit.image else "/static/img/placeholder.png",
                    a.produit.nom,
                    a.quantite,
                    a.prix * a.quantite,
                )
                for a in articles
            )
        )
    articles_affiches.short_description = "Articles"


# -----------------------------------------
# Produit Admin
# -----------------------------------------

class ProduitAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Produit
        fields = '__all__'


class ProduitAdmin(admin.ModelAdmin):
    form = ProduitAdminForm
    list_display = ('nom', 'categorie', 'prix', 'stock', 'actif', 'image_preview')
    search_fields = ('nom',)
    list_filter = ('categorie', 'actif')
    list_editable = ('prix', 'stock', 'actif')
    readonly_fields = ('image_preview',)

    class Media:
        js = ('js/image_preview.js',)  # Assure-toi que ce fichier JS existe et est chargé correctement

    def image_preview(self, obj):
        """
        Affiche un aperçu de l'image du produit dans l'admin.
        Si aucune image, on affiche une balise vide masquée.
        """
        if obj.image:
            return format_html(
                '<img id="img-preview" src="{}" width="150" height="150" '
                'style="object-fit:cover; border-radius:10px;" />',
                obj.image.url
            )
        return format_html('<img id="img-preview" width="150" style="display:none;" />')

    image_preview.short_description = 'Aperçu'


# -----------------------------------------
# Register Models
# -----------------------------------------

admin.site.register(Client)
admin.site.register(Produit, ProduitAdmin)
admin.site.register(Categorie)
admin.site.register(Commande, CommandeAdmin)
admin.site.register(ArticleCommande)
