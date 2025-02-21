from django.db import models
from Connexion.models import CustomUser

class RegimeAlimentaire(models.Model):
    nom = models.CharField(max_length=200)  # Réduit de 50 à 40
    description = models.TextField()

    def __str__(self):
        return self.nom

class Category(models.Model):
    nom = models.CharField(max_length=200)  # Réduit de 50 à 40
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_ajout']

    def __str__(self):
        return self.nom

class Product(models.Model):
    name = models.CharField(max_length=200, db_index=True)  # Réduit de 50 à 40
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    regime = models.ForeignKey(RegimeAlimentaire, related_name='products', on_delete=models.CASCADE, null=True)
    smalldescription = models.CharField(max_length=300)  # Réduit de 60 à 50
    description = models.TextField()
    photo = models.ImageField(upload_to='images/', blank=True)
    status = models.CharField(max_length=100, null=True)  # Réduit de 50 à 40
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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)  # Relation avec l'utilisateur
    nom = models.CharField(max_length=200)
    prenom = models.CharField(max_length=200)
    email = models.EmailField()
    address = models.CharField(max_length=200)
    addressli = models.CharField(max_length=200, null=True)
    contact = models.CharField(max_length=20)
    ville = models.CharField(max_length=200)
    numero_destinataire = models.CharField(max_length=200, null=True)
    nom_prenom_destinataire = models.CharField(max_length=200, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    date_commande = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=150, choices=STATUS_CHOICES, default='pending')  # Nouveau champ

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
    regime_alimentaire_prefere = models.CharField(max_length=90, choices=[  # Réduit de 70 à 20
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
    nom = models.CharField(max_length=200)  # Réduit de 60 à 40
    email = models.EmailField()
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_envoi']

    def __str__(self):
        return self.nom

class Article(models.Model) :
    title = models.CharField(max_length=200)
    Smalldescription = models.TextField(null=True)
    description = models.TextField()
    image = models.ImageField(upload_to='images/')
    date_add = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_add']

    def __str__(self):
        return self.title


