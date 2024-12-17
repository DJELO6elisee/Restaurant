from django.urls import path
from .views import index, produit, panini, sup_catego, detailPro, elisee, contact, confirmation, adminp, table, creation, productlist, modification, delete_product, commande, detailCommande, message, delete_commande, category, create_cat, modif_cat


urlpatterns = [

    path('', index, name='shop'),
    path('articles/', produit, name='produit'),
    path('panini/', panini, name='panini'),
    path('elisee/', elisee, name='elisee'),
    path('contact/', contact, name='contact'),
    path('confirmation/<int:conf_id>/', confirmation, name='confirmation'),
    path('adminp/', adminp, name='adminp'),
    path('table/', table, name='table'),
    path('creation/', creation, name='creation'),
    path('productlist/', productlist, name='productlist'),
    path('commande/', commande, name='commande'),
    path('message/', message, name='message'),
    path('category/', category, name='category'),
    path('create_cat/', create_cat, name='create_cat'),
    path('detailPro/<int:de_id>/', detailPro, name='detailPro'),

    
    path('detailComande/<int:commande_id>/', detailCommande, name='detailComande'),

    path('modification/<int:product_id>/', modification, name='modification'),
    path('modif_cat/<int:cat_id>/', modif_cat, name='modif_cat'),
    path('sup_catego/<int:delsup_id>/', sup_catego, name='sup_catego'),
    path('delete_product/<int:product_id>/', delete_product, name='delete_product'),
    path('delete_commande/<int:commande_id>/', delete_commande, name='delete_commande'),
]