from django.contrib import admin
from .models import Product, Category, Commande, DetailCommande, Message

class AdminProduct(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'smalldescription', 'description', 'date_creation', 'photo')

class AdminCommande(admin.ModelAdmin):
    list_display = ('items', 'nom', 'prenom', 'email', 'address', 'contact', 'ville', 'total', 'date_commande')
# Register your models here.
class AdminDetailCommande(admin.ModelAdmin):
    list_display = ('commande', 'product', 'quantite', 'prix_total')

class AdminMessage(admin.ModelAdmin):
    list_display = ('nom', 'email', 'message', 'date_envoi')

admin.site.register(Product, AdminProduct)
admin.site.register(Category)
admin.site.register(Commande, AdminCommande)

admin.site.register(DetailCommande)
admin.site.register(Message, AdminMessage)
