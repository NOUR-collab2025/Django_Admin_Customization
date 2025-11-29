from django.contrib import admin
from django.contrib.admin import AdminSite
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.utils.html import format_html, format_html_join
from django import forms
from ckeditor.widgets import CKEditorWidget
from django.contrib.admin import widgets
from django.shortcuts import render
from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from .models import Commande, ArticleCommande


from .models import Client, Produit, Categorie, Commande, ArticleCommande

#@staff_member_required
def dashboard_view(request):
    total_clients = Client.objects.count()
    total_commandes = Commande.objects.count()
    total_produits = Produit.objects.count()
    
    commandes_par_statut = (
        Commande.objects.values('statut')
        .order_by('statut')
        .annotate(count=models.Count('id'))
    )

    context = {
        'total_clients': total_clients,
        'total_commandes': total_commandes,
        'total_produits': total_produits,
        'commandes_par_statut': commandes_par_statut,
    }
    dernieres_commandes = Commande.objects.order_by('-cree_le')[:5]
    produits_faible_stock = Produit.objects.filter(stock__lt=5)
    context.update({
        'dernieres_commandes': dernieres_commandes,
        'produits_faible_stock': produits_faible_stock
    })
    return render(request, 'admin/dashboard.html', context)


# ------------------- Custom AdminSite -------------------
class CustomAdminSite(AdminSite):
    site_header = "Mon Administration"
    site_title = "Dashboard"
    index_title = "Bienvenue sur le tableau de bord"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls
    



# ------------------- Inline ArticleCommande -------------------
class ArticleCommandeInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        has_article = any(
            form.cleaned_data and not form.cleaned_data.get('DELETE', False)
            for form in self.forms
        )
        if not has_article:
            raise ValidationError("Vous devez ajouter au moins un produit à la commande.")


class ArticleCommandeInline(admin.TabularInline):
    model = ArticleCommande
    extra = 1
    autocomplete_fields = ('produit',)
    formset = ArticleCommandeInlineFormSet


# ------------------- CommandeAdmin -------------------
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
    readonly_fields_existing = ('client',)

    class Media:
        js = ('js/commande_admin.js',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save()
        form.instance.calculer_total()

    def articles_affiches(self, obj):
        articles = obj.articlecommande_set.all()
        if not articles:
            return "-"
        return format_html_join(
            '<br>',
            '<img src="{}" width="40" height="40" style="object-fit:cover; margin-right:5px;"> {} x {} = {} DT',
            (
                (
                    a.produit.image.url if a.produit.image else '/static/img/placeholder.png',
                    a.produit.nom,
                    a.quantite,
                    a.prix * a.quantite
                )
                for a in articles
            )
        )
    articles_affiches.short_description = 'Articles'


# ------------------- ProduitAdmin -------------------
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
        js = ('js/image_preview.js',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img id="img-preview" src="{}" width="150" height="150" style="object-fit:cover; border-radius:10px;" />',
                obj.image.url
            )
        return format_html('<img id="img-preview" width="150" style="display:none;" />')
    image_preview.short_description = 'Aperçu'


# ------------------- CategorieAdmin -------------------
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description', 'cree_le', 'modifie_le')


# ------------------- ClientAdmin -------------------
class ClientAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'email', 'telephone', 'adresse')
    search_fields = ('prenom', 'nom', 'email')


# ------------------- Création de l'admin personnalisé -------------------
admin_site = CustomAdminSite(name='custom_admin')

# Enregistrement des modèles
admin_site.register(Client, ClientAdmin)
admin_site.register(Produit, ProduitAdmin)
admin_site.register(Categorie, CategorieAdmin)
admin_site.register(Commande, CommandeAdmin)

admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
