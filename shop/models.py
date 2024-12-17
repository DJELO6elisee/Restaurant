from django.db import models
from Connexion.models import CustomUser
# Create your models here.


class RegimeAlimentaire(models.Model):
    nom = models.CharField(max_length=100)  # Exemple : "Vegan", "Sans gluten"
    description = models.TextField()

    def __str__(self):
        return self.nom


class Category(models.Model):
    nom = models.CharField(max_length=200)
    date_ajout = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_ajout']

    def __str__(self):
        return str(self.nom)


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    category = models.ForeignKey(Category, related_name='categories', on_delete=models.CASCADE)
    regime = models.ForeignKey(RegimeAlimentaire, related_name='regimes', on_delete=models.CASCADE, null=True)
    smalldescription = models.CharField(max_length=300)
    description = models.TextField()
    photo = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.CharField(max_length=100)
    produit_frais = models.BooleanField(default=False)
    produit_bio = models.BooleanField(default=False)
    produit_vegan = models.BooleanField(default=False)
    produit_sans_gluten = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now=True)



    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return str(self.name)


class Commande(models.Model):
    items = models.CharField(max_length=200)
    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150, null=True)
    email = models.EmailField()
    address = models.CharField(max_length=200)
    contact = models.IntegerField()
    ville = models.CharField(max_length=200)
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Utilisé pour des montants financiers

    date_commande = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_commande']

    def __str__(self):
        return self.nom


class DetailCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Le prix du produit
    prix_total = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.URLField(default='http//photo')  # URL de l'image du produit

    def __str__(self):
        return f"{self.quantite} x {self.product.name} - Commande {self.commande.id}"


class Message(models.Model):
    nom = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_envoi']

    def __str__(self):
        return str(self.nom)
    

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_achat = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} purchased {self.product.name} on {self.date_achat}"


class ProfileUtilisateur(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    regime_alimentaire_prefere = models.CharField(max_length=100, choices=[('vegan', 'Vegan'), ('végétarien', 'Végétarien'), ('sans_gluten', 'Sans-Gluten'), ('paléolithique_(Paleo)', 'Paléolithique_(Paleo)'), ('méditerranéen', 'Mediterranéen'), ('cétogène_(Keto)','Cétogène_(Keto)')])
    preferred_categories = models.ManyToManyField(Category)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
