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

    def mark_as_expedie(self, request, queryset):
        queryset.update(statut='expedie')
        self.message_user(request, f"{queryset.count()} commande(s) marquée(s) comme expédiée(s).")
    mark_as_expedie.short_description = "Marquer les commandes sélectionnées comme expédié"

    # Action pour marquer plusieurs commandes comme "terminé"
    def mark_as_termine(self, request, queryset):
        queryset.update(statut='termine')
        self.message_user(request, f"{queryset.count()} commande(s) marquée(s) comme terminée(s).")
    mark_as_termine.short_description = "Marquer les commandes sélectionnées comme terminé"

    def mark_as_en_attente(self, request, queryset):
        queryset.update(statut='en attente')
        self.message_user(request, f"{queryset.count()} commande(s) marquée(s) comme en attente.")
    mark_as_en_attente.short_description= "Marquer les commandes sélectionnées comme en attente"

    def mark_as_annule(self, request, queryset):
        queryset.update(statut='annulé')
        self.message_user(request, f"{queryset.count()} commande(s) marquée(s) comme annulée(s).")
    mark_as_annule.short_description= "Marquer les commandes sélectionnées comme annulé"

    def mark_as_en_cours(self, request, queryset):
        queryset.update(statut='en cours')
        self.message_user(request, f"{queryset.count()} commande(s) marquée(s) comme en cours.")
    mark_as_en_cours.short_description= "Marquer les commandes sélectionnées comme en cours"

    # Ajouter les actions dans la liste d'actions disponibles
    actions = ['mark_as_expedie', 'mark_as_termine', 'mark_as_en_attente', 'mark_as_annule', 'mark_as_en_cours']


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

    def mark_as_active(self, request, queryset):
        queryset.update(actif=True)  # Change le champ 'actif' de tous les objets sélectionnés
        self.message_user(request, f"{queryset.count()} produit(s) marqué(s) comme actif(s).")
    mark_as_active.short_description = "Marquer les produits sélectionnés comme actif"

    def mark_as_inactive(self, request, queryset):
        queryset.update(actif=False)
        self.message_user(request, f"{queryset.count()} produit(s) marqué(s) comme inactif(s).")
    mark_as_inactive.short_description = "Marquer les produits sélectionnés comme inactif"

    # Ajouter les actions dans la liste d'actions disponibles
    actions = ['mark_as_active', 'mark_as_inactive']


# -----------------------------------------
# Register Models
# -----------------------------------------

admin.site.register(Client)
admin.site.register(Produit, ProduitAdmin)
admin.site.register(Categorie)
admin.site.register(Commande, CommandeAdmin)
admin.site.register(ArticleCommande)