from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager  # Assurez-vous d'utiliser le gestionnaire personnalisé
    
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=20, blank=True, null=True)

    USERNAME_FIELD = 'email'  # Utiliser l'email comme identifiant
    REQUIRED_FIELDS = []  # Laisser vide car 'username' est remplacé par 'email'
    first_name = models.CharField(max_length=30, blank=True)  # Réduit de 40 à 30

    objects = CustomUserManager()  # Utiliser le gestionnaire personnalisé pour la gestion des utilisateurs

    def __str__(self):
        return self.email