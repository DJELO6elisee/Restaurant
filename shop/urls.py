from django.urls import path
from .views import index, produit, recu, panini, profile, recuCommande, profile_edit, sup_catego, detailPro, elisee, contact, detail_commandeUti, confirmation, historique_commande, adminp, table, creation, productlist, modification, delete_product, commande, detailCommande, message, delete_commande, category, create_cat, modif_cat, regime, create_regime, modif_regime, sup_regime


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
    path('regime/', regime, name='regime'),
    path('profile/', profile, name='profile'),
    path('profile_edit/', profile_edit, name='profile_edit'),

    path('create_cat/', create_cat, name='create_cat'),
    path('create_regime/', create_regime, name='create_regime'),
    path('historique_commande/', historique_commande, name='historique_commande'),
    path('detailPro/<int:de_id>/', detailPro, name='detailPro'),
    path('detail_commandeUti/<int:commande_id>/', detail_commandeUti, name='detail_commandeUti'),
    path('recu/<int:com_id>/', recu, name='recu'),

    path('recuCommande/<int:recu_id>/', recuCommande, name='recuCommande'),


    path('detailComande/<int:commande_id>/', detailCommande, name='detailComande'),

    path('modification/<int:product_id>/', modification, name='modification'),
    path('modif_cat/<int:cat_id>/', modif_cat, name='modif_cat'),

    path('modif_regime/<int:regi_id>/', modif_regime, name='modif_regime'),

    path('sup_regime/<int:delre_id>/', sup_regime, name='sup_regime'),

    path('sup_catego/<int:delsup_id>/', sup_catego, name='sup_catego'),
    path('delete_product/<int:product_id>/', delete_product, name='delete_product'),
    path('delete_commande/<int:commande_id>/', delete_commande, name='delete_commande'),
]