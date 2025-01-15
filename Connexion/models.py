from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager  # Assurez-vous d'utiliser le gestionnaire personnalisé

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=200, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    contact = models.CharField(max_length=15, blank=True, null=True)  # Numéro de téléphone
    adresse = models.CharField(max_length=300, blank=True, null=True)  # Adresse personnelle
    adresse_livraison = models.CharField(max_length=300, blank=True, null=True)  # Adresse de livraison

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    first_name = models.CharField(max_length=200, blank=True)
    objects = CustomUserManager()

    def __str__(self):
        return self.email