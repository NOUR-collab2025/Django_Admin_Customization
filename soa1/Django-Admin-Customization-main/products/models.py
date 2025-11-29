from django.db import models
from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError


# ------------------- Categorie -------------------
class Categorie(models.Model):
    nom = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categorie'
        ordering = ['nom']
        verbose_name_plural = 'Catégories'

    def __str__(self):
        return self.nom


# ------------------- Produit -------------------
class Produit(models.Model):
    nom = models.CharField(max_length=255)
    description = RichTextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='produits')
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'produit'
        ordering = ['nom']
        verbose_name_plural = 'Produits'

    def __str__(self):
        return self.nom


# ------------------- Client -------------------
class Client(models.Model):
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'client'
        ordering = ['nom', 'prenom']
        verbose_name_plural = 'Clients'

    def __str__(self):
        return f"{self.prenom} {self.nom}"


# ------------------- Commande -------------------
class Commande(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    statut = models.CharField(max_length=20, choices=(
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('expedie', 'Expédié'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé')),
        default='en_attente'
    )
    prix_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    def calculer_total(self):
        total = sum(item.prix * item.quantite for item in self.articlecommande_set.all())
        self.prix_total = total
        self.save()
    def clean(self):
        if self.pk:  # commande existe déjà
            if self.articlecommande_set.count() == 0:
                raise ValidationError("Une commande doit avoir au moins un produit.")

    def save(self, *args, **kwargs):
        self.full_clean()  # appelle clean avant save
        super().save(*args, **kwargs)
    def __str__(self):
        return f"Commande #{self.id}"


# ------------------- ArticleCommande -------------------
class ArticleCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.prix = self.produit.prix
        super().save(*args, **kwargs)
        self.commande.calculer_total()

    def __str__(self):
        return f"{self.produit.nom} x{self.quantite}"
    
