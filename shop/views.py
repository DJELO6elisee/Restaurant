from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest
from django.db.models import Sum
# import logging

from .models import Product, Category, Commande, DetailCommande, Message, RegimeAlimentaire
import json
from django.contrib.auth.decorators import login_required
from Connexion.models import CustomUser
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
def panini(request):
    return render(request, 'shop/panini.html')

# logger = logging.getLogger(__name__)

@login_required(login_url='connexion')
def confirmation(request, conf_id):
    commande = get_object_or_404(Commande, id=conf_id)
    return render(request, 'shop/confirmation.html', {'commande': commande})

@login_required(login_url='connexion')
def elisee(request):
    user = request.user
    if request.method == "POST":
        # Récupérer les informations du formulaire
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        ville = request.POST.get('ville')
        address = request.POST.get('address')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        total = request.POST.get('total')

        # Valider les données du formulaire
        if not (nom and prenom and ville and address and contact and email and total):
            return HttpResponseBadRequest("Tous les champs sont requis.")

        # Récupérer et valider les données du panier
        try:
            panier_data = json.loads(request.POST.get('panier', '[]'))  # Par défaut, un tableau vide
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Données du panier invalides.")

        # Vérifier que le panier contient des produits
        if not panier_data:
            return HttpResponseBadRequest("Le panier est vide.")

        # Créer une nouvelle commande
        commande = Commande.objects.create(
            nom=nom,
            prenom=prenom,
            ville=ville,
            address=address,
            contact=contact,
            email=email,
            total=total
        )

        # Parcourir les éléments du panier et créer les détails de la commande
        for item in panier_data:
            try:
                # Récupérer l'ID et valider
                product_id = item.get('id')
                if not product_id:
                    continue  # Ignorer les produits sans ID

                # Récupérer le produit correspondant
                product = Product.objects.get(id=product_id)

                # Calculer le prix total de l'article
                prix_total = item['prix'] * item['quantite']

                # Créer le détail de commande
                DetailCommande.objects.create(
                    commande=commande,
                    product=product,
                    quantite=item['quantite'],
                    prix=item['prix'],
                    image=item['photo'],
                    prix_total=prix_total
                )
            except Product.DoesNotExist:
                # Ignorer les produits non trouvés
                continue
            except KeyError:
                # Ignorer les données mal formées
                continue

        # Rediriger vers la page de confirmation
        return redirect('confirmation', conf_id=commande.id)

    return render(request, 'shop/checkout.html', {'user': user})

def contact(request):
    saveMessage = None  # Initialisation de la variable pour éviter les erreurs
    if request.method == 'POST':
        nom = request.POST.get('nom', '')
        email = request.POST.get('email', '')
        message = request.POST.get('message', '')

        # Sauvegarde du message
        saveMessage = Message.objects.create(nom=nom, email=email, message=message)

    return render(request, 'shop/contact.html', {'saveMessage': saveMessage})

def message(request):
    messag = Message.objects.all()

    # Renvoyer les données au template
    return render(request, 'shop/message.html', {'messag': messag})

def index(request):
    produits_sous = Product.objects.filter(status='acceuil')

    # Gestion de la recherche
    query = request.GET.get('item_name')  # Récupère la requête de recherche depuis les paramètres GET
    search_results = []

    if query:
        # Rechercher dans tous les produits selon le nom
        search_results = Product.objects.filter(name__icontains=query)
    return render(request, 'shop/index.html', {'produits_sous': produits_sous, 'search_results': search_results, 'query':query })

from django.db.models import Count


def get_recommendations(user_email):
    if not user_email:
        return []

    # Récupérer les commandes de l'utilisateur
    commandes = Commande.objects.filter(email=user_email).prefetch_related('details__product')

    if not commandes.exists():
        return []

    # Récupérer les produits achetés
    product_ids = DetailCommande.objects.filter(commande__in=commandes).values_list('product_id', flat=True)

    # Identifier les catégories les plus populaires
    category_counts = (
        DetailCommande.objects.filter(product_id__in=product_ids)
        .values('product__category')
        .annotate(count=Count('product__category'))
        .order_by('-count')
    )

    if not category_counts:
        return []

    most_common_category_id = category_counts[0]['product__category']

    # Recommander des produits dans cette catégorie
    recommended_products = Product.objects.filter(category_id=most_common_category_id).exclude(id__in=product_ids)

    # Vérification que les produits recommandés ont des IDs valides
    recommended_products = [product for product in recommended_products if product.id]

    return recommended_products

def produit(request):
    # Récupérer toutes les catégories sauf la première
    categories = Category.objects.all()[1:]

    # Récupérer les régimes alimentaires et les filtres depuis l'URL
    regimes = request.GET.getlist('regime') or []  # Si aucun régime n'est sélectionné, utiliser une liste vide
    produit_frais = request.GET.get('produit_frais')
    produit_bio = request.GET.get('produit_bio')
    produit_vegan = request.GET.get('produit_vegan')
    produit_sans_gluten = request.GET.get('produit_sans_gluten')

    # Préparer une liste pour stocker les catégories avec leurs produits filtrés
    categories_with_products = []

    for category in categories:
        # Récupérer les produits associés à la catégorie
        produits_in_category = Product.objects.filter(category=category)

        # Appliquer les filtres des régimes alimentaires
        if regimes:
            produits_in_category = produits_in_category.filter(regime__nom__in=regimes)

        # Appliquer les filtres de produit frais, bio, vegan, sans gluten
        if produit_frais:
            produits_in_category = produits_in_category.filter(produit_frais=True)
        if produit_bio:
            produits_in_category = produits_in_category.filter(produit_bio=True)
        if produit_vegan:
            produits_in_category = produits_in_category.filter(produit_vegan=True)
        if produit_sans_gluten:
            produits_in_category = produits_in_category.filter(produit_sans_gluten=True)

        # Si des produits existent dans cette catégorie après le filtrage, on ajoute la catégorie et ses produits
        if produits_in_category.exists():
            categories_with_products.append({
                'category': category,
                'products': produits_in_category
            })

    # Recommandations de produits (optionnel)
    recommended_products = []
    if request.user.is_authenticated:
        recommended_products = get_recommendations(request.user.email)

    # Gestion de la recherche
    query = request.GET.get('item_name')  # Récupère la requête de recherche depuis les paramètres GET
    search_results = []

    if query:
        # Rechercher dans tous les produits selon le nom
        search_results = Product.objects.filter(name__icontains=query)

    return render(request, 'shop/produit.html', {
        'categories_with_products': categories_with_products,
        'recommended_products': recommended_products,
        'search_results': search_results,
        'query': query,
    })

@login_required(login_url='connexion')
def adminp(request):
    command = Commande.objects.all()[:7]
    commandes = Commande.objects.all()
    messag = Message.objects.all()

    # Compter le nombre total de messages
    total_messages = messag.count()

    # Compter le nombre de commandes
    total_commandes = commandes.count()
    somme_totaux = commandes.aggregate(Sum('total'))['total__sum'] or 0
    total_users = CustomUser.objects.count()

    # Renvoyer les données au template
    return render(request, 'shop/indexx.html', {'command': command, 'commandes': commandes, 'total_commandes': total_commandes, 'somme_totaux': somme_totaux, 'messag': messag, 'total_messages': total_messages, 'total_users': total_users})

@login_required(login_url='connexion')
def table(request):
    return render(request, 'shop/tables.html')

@login_required(login_url='connexion')
def creation(request):
    if request.method == "POST":
        # Récupérer les données du formulaire
        name = request.POST.get("name")
        price = request.POST.get("price")
        category_id = request.POST.get("category")
        regime_id = request.POST.get("regime")  # Récupérer le régime alimentaire
        smalldescription = request.POST.get("smalldescription")
        description = request.POST.get("description")
        photo = request.FILES.get("photo")
        status = request.POST.get("status")

        produit_frais = 'produit_frais' in request.POST  # Si la case est cochée
        produit_bio = 'produit_bio' in request.POST
        produit_vegan = 'produit_vegan' in request.POST
        produit_sans_gluten = 'produit_sans_gluten' in request.POST

        # Valider que la catégorie existe
        try:
            category = Category.objects.get(id=category_id)
        except ObjectDoesNotExist:
            messages.error(request, "La catégorie sélectionnée est invalide.")
            return redirect("creation")

        # Valider que le régime existe
        try:
            regime = RegimeAlimentaire.objects.get(id=regime_id)
        except ObjectDoesNotExist:
            messages.error(request, "Le régime alimentaire sélectionné est invalide.")
            return redirect("creation")

        # Créer le produit
        product = Product(
            name=name,
            price=price,
            category=category,
            regime=regime,  # Assigner le régime alimentaire sélectionné
            smalldescription=smalldescription,
            description=description,
            photo=photo,
            status=status,
            produit_frais=produit_frais,
            produit_bio=produit_bio,
            produit_vegan=produit_vegan,
            produit_sans_gluten=produit_sans_gluten
        )
        product.save()  # Sauvegarder dans la base de données

        messages.success(request, "Produit créé avec succès !")
        return redirect("productlist")  # Rediriger vers la liste des produits (ou une autre page)

    # Si GET, afficher le formulaire
    categories = Category.objects.all()  # Charger les catégories disponibles
    regimes = RegimeAlimentaire.objects.all()  # Charger les régimes alimentaires disponibles
    return render(request, 'shop/creation.html', {"categories": categories, "regimes": regimes})

@login_required(login_url='connexion')
def productlist(request):
    product = Product.objects.all()

    return render(request, 'shop/productlist.html', {'product': product})

@login_required(login_url='connexion')
def modification(request, product_id):
    # Récupérer le produit à modifier
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()  # Liste des catégories disponibles

    if request.method == 'POST':
        # Traitement du formulaire avec les données envoyées (et photo si présente)
        name = request.POST.get('name')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        smalldescription = request.POST.get('smalldescription')
        description = request.POST.get('description')
        photo = request.FILES.get('photo')
        status = request.POST.get('status')

        category_instance = get_object_or_404(Category, id=category_id)

        # Mise à jour du produit avec les nouvelles données
        product.name = name
        product.price = price
        product.category = category_instance    # Associe la catégorie en fonction de l'ID
        product.smalldescription = smalldescription
        product.description = description
        if photo:
            product.photo = photo  # Si une nouvelle photo est téléchargée, on la remplace
        product.status = status
        product.save()

        # Redirection après modification
        return redirect('productlist')  # Redirigez vers la liste des produits (ajustez l'URL selon votre projet)

    # Si la méthode est GET, afficher le formulaire avec les données actuelles du produit
    context = {
        'product': product,
        'categories': categories,
    }

    return render(request, 'shop/modification.html', context)

@login_required(login_url='connexion')
def delete_product(request, product_id):
    # Récupérer le produit à supprimer
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Supprimer le produit
        product.delete()
        return redirect('productlist')  # Rediriger vers la liste des produits après suppression

    # Si la méthode est GET, afficher une confirmation
    return render(request, 'shop/confirm_delete.html', {'product': product})


@login_required(login_url='connexion')
def delete_commande(request, commande_id):
    # Récupérer le produit à supprimer
    del_commande = get_object_or_404(Commande, id=commande_id)

    if request.method == 'POST':
        # Supprimer le produit
        del_commande.delete()
        return redirect('commande')  # Rediriger vers la liste des produits après suppression

    # Si la méthode est GET, afficher une confirmation
    return render(request, 'shop/delete_commande.html', {'del_commande': del_commande})

def send_status_update_email(commande):
    subject = f"Statut de votre commande #{commande.id} mis à jour"
    message = f"Bonjour {commande.nom},\n\nLe statut de votre commande a été mis à jour.\n\nStatut actuel : {commande.get_status_display()}."
    from_email = 'jeaneliseedjelo85@gmail.com'  # Adresse email par défaut
    recipient_list = [commande.email]  # Liste des destinataires (ici l'email de l'utilisateur)

    # Envoi de l'email
    send_mail(subject, message, from_email, recipient_list)



@login_required(login_url='connexion')
def commande(request):
    commandes = Commande.objects.all()

    if request.method == 'POST':
        commande_id = request.POST.get('commande_id')
        status = request.POST.get('status')

        commande = Commande.objects.get(id=commande_id)
        previous_status = commande.status  # On peut garder l'ancien statut si nécessaire
        commande.status = status
        commande.save()

        # Ajouter un message pour l'utilisateur
        messages.success(request, f"Le statut de votre commande a été mis à jour en '{status}'.")

        # Si vous souhaitez envoyer un message par email à l'utilisateur
        if previous_status != status:
            send_status_update_email(commande)

        return redirect('commande')  # Rediriger vers la page des commandes après la mise à jour

    context = {
        'commandes': commandes
    }
    return render(request, 'shop/commande.html', context)


@login_required(login_url='connexion')
def detailCommande(request, commande_id):
    # Récupérer la commande en fonction de l'ID
    commande = get_object_or_404(Commande, id=commande_id)

    # Récupérer les détails associés à cette commande uniquement
    details_commande = DetailCommande.objects.filter(commande=commande)

    # Contexte pour le template
    context = {
        'commande': commande,
        'details_commande': details_commande
    }

    # Rendre le template avec les données
    return render(request, 'shop/detailCommande.html', context)

def category(request):
    categories = Category.objects.all()

    return render(request, 'shop/category.html', {'categories': categories})

def create_cat(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')

        categori = Category(nom=nom)
        categori.save()
    return render(request, 'shop/create_categorie.html')

def modif_cat(request, cat_id):
    catego = get_object_or_404(Category, id=cat_id)

    if request.method == 'POST':
        nom = request.POST.get('nom')

        catego.nom = nom
        catego.save()
        return redirect('category')

    return render(request, 'shop/modif_categorie.html', {'catego': catego})

def sup_catego(request, delsup_id):
    del_cat = get_object_or_404(Category, id=delsup_id)
    if request.method == 'POST':
        del_cat.delete()
        return redirect('category')
    return render(request, 'shop/sup_categorie.html', {'del_cat': del_cat})



def detailPro(request, de_id):
    detailpro = get_object_or_404(Product, id=de_id)

    related_products = Product.objects.filter(category=detailpro.category).exclude(id=detailpro.id)[:4]  # Limiter à 4 produits

    return render(request, 'shop/detailPro.html', {'detailpro': detailpro, 'related_products': related_products})



def regime(request):
    regimes = RegimeAlimentaire.objects.all()

    return render(request, 'shop/regime.html', {'regimes': regimes})

def create_regime(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')

        regime = RegimeAlimentaire(nom=nom)
        regime.save()
    return render(request, 'shop/regime_create.html')

def modif_regime(request, regi_id):
    regi = get_object_or_404(RegimeAlimentaire, id=regi_id)

    if request.method == 'POST':
        nom = request.POST.get('nom')

        regi.nom = nom
        regi.save()
        return redirect('regime')

    return render(request, 'shop/regime_update.html', {'regi': regi})

def sup_regime(request, delre_id):
    del_regi = get_object_or_404(RegimeAlimentaire, id=delre_id)
    if request.method == 'POST':
        del_regi.delete()
        return redirect('regime')
    return render(request, 'shop/regime_delete.html', {'del_regi': del_regi})

def historique_commande(request):
    # Filtrer les commandes de l'utilisateur connecté
    commandes = Commande.objects.filter(email=request.user.email)

    context = {
        'commandes': commandes
    }
    return render(request, 'shop/historique_commande.html', context)

@login_required
def detail_commandeUti(request, commande_id):
    # Récupérer les détails d'une commande spécifique
    commande = get_object_or_404(Commande, id=commande_id)
    # Assurez-vous que l'utilisateur est autorisé à voir cette commande
    if commande.email != request.user.email:
        return redirect('historique_commande')  # Rediriger si l'utilisateur tente d'accéder à une commande qui ne lui appartient pas

    # Récupérer les détails de la commande (produits associés)
    details_commande = commande.details.all()

    context = {
        'commande': commande,
        'details_commande': details_commande
    }
    return render(request, 'shop/detail_commandeU.html', context)








