from django.urls import path
from .views import index, produit, panini, elisee, contact, confirmation, admin, table, creation, productlist, modification, delete_product, commande, detailCommande, message


urlpatterns = [
    path('', index, name='shop'),
    path('articles/', produit, name='produit'),
    path('panini/', panini, name='panini'),
    path('elisee/', elisee, name='elisee'),
    path('contact/', contact, name='contact'),
    path('confirmation/', confirmation, name='confirmation'),
    path('adminp/', admin, name='adminp'),
    path('table/', table, name='table'),
    path('creation/', creation, name='creation'),
    path('productlist/', productlist, name='productlist'),
    path('commande/', commande, name='commande'),
    path('message/', message, name='message'),

    
    path('detailComande/<int:commande_id>/', detailCommande, name='detailComande'),

    path('modification/<int:product_id>/', modification, name='modification'),
    path('delete_product/<int:product_id>/', delete_product, name='delete_product'),
]