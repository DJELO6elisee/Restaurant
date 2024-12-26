from django.db import models
from Connexion.models import CustomUser

class RegimeAlimentaire(models.Model):
    nom = models.CharField(max_length=40)  # Réduit de 50 à 40
    description = models.TextField()

    def __str__(self):
        return self.nom

class Category(models.Model):
    nom = models.CharField(max_length=40)  # Réduit de 50 à 40
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_ajout']

    def __str__(self):
        return self.nom

class Product(models.Model):
    name = models.CharField(max_length=40, db_index=True)  # Réduit de 50 à 40
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    regime = models.ForeignKey(RegimeAlimentaire, related_name='products', on_delete=models.CASCADE, null=True)
    smalldescription = models.CharField(max_length=50)  # Réduit de 60 à 50
    description = models.TextField()
    photo = models.ImageField(upload_to='images/', blank=True)
    status = models.CharField(max_length=40)  # Réduit de 50 à 40
    produit_frais = models.BooleanField(default=False)
    produit_bio = models.BooleanField(default=False)
    produit_vegan = models.BooleanField(default=False)
    produit_sans_gluten = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return self.name

class Commande(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours de traitement'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
    ]
    items = models.CharField(max_length=20)
    nom = models.CharField(max_length=40)
    prenom = models.CharField(max_length=40)
    email = models.EmailField()
    address = models.CharField(max_length=40)
    contact = models.CharField(max_length=15)
    ville = models.CharField(max_length=40)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    date_commande = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='delivered')  # Nouveau champ

    class Meta:
        ordering = ['-date_commande']

    def __str__(self):
        return f"Commande {self.id} - {self.nom} ({self.get_status_display()})"


class DetailCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    prix_total = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.URLField(default='http://photo')

    def __str__(self):
        return f"{self.quantite} x {self.product.name} - Commande {self.commande.id}"



class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_achat = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} purchased {self.product.name} on {self.date_achat}"
class ProfileUtilisateur(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    regime_alimentaire_prefere = models.CharField(max_length=20, choices=[  # Réduit de 70 à 20
        ('vegan', 'Vegan'),
        ('vegetarien', 'Végétarien'),
        ('sans_gluten', 'Sans-Gluten'),
        ('paleolithique', 'Paléolithique (Paleo)'),
        ('mediterraneen', 'Méditerranéen'),
        ('cetogene', 'Cétogène (Keto)')
    ])
    preferred_categories = models.ManyToManyField(Category)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Message(models.Model):
    nom = models.CharField(max_length=40)  # Réduit de 60 à 40
    email = models.EmailField()
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_envoi']

    def __str__(self):
        return self.nom

