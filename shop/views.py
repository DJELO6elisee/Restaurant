from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest
from django.db.models import Sum
# import logging

from django.contrib import messages


from .models import Product, Category, Commande, DetailCommande, Message
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from Connexion.models import CustomUser


# Create your views here.
@login_required(login_url='connexion')
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

@login_required(login_url='connexion')
def contact(request):
    saveMessage = None  # Initialisation de la variable pour éviter les erreurs
    if request.method == 'POST':
        nom = request.POST.get('nom', '')
        email = request.POST.get('email', '')
        message = request.POST.get('message', '')

        # Sauvegarde du message
        saveMessage = Message.objects.create(nom=nom, email=email, message=message)

    return render(request, 'shop/contact.html', {'saveMessage': saveMessage})

@login_required(login_url='connexion')
def message(request):
    messag = Message.objects.all()

    # Renvoyer les données au template
    return render(request, 'shop/message.html', {'messag': messag})

@login_required(login_url='connexion')
def index(request):
    produits_sous = Product.objects.filter(status='acceuil')

    return render(request, 'shop/index.html', {'produits_sous': produits_sous})

@login_required(login_url='connexion')
def produit(request):
    # produits_sous = Product.objects.filter(status='sous')[:4]

    categories = Category.objects.all()[1:]

    # Récupérer les produits associés à chaque catégorie
    categories_with_products = []
    for category in categories:
        produits_in_category = Product.objects.filter(category=category)
        categories_with_products.append({'category': category, 'products': produits_in_category})

    return render(request, 'shop/produit.html', {'categories_with_products': categories_with_products})


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

# def create(request):
#     if request.method == 'POST':
#         # Récupérer les données du formulaire avec .get()
#         username = request.POST.get('username')
#         first_name = request.POST.get('first_name')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         password_confirm = request.POST.get('password_confirm')

#         # Stocker les valeurs valides dans un dictionnaire pour les réutiliser
#         form_data = {
#             'username': username,
#             'first_name': first_name,
#             'email': email,
#         }

#         # Initialiser une variable pour suivre les erreurs
#         errors = False

#         # Vérifier si tous les champs sont remplis
#         if not username or not first_name or not email or not password or not password_confirm:
#             messages.error(request, "Tous les champs doivent être remplis.")
#             errors = True

#         # Vérifier si les mots de passe sont identiques
#         if password != password_confirm:
#             messages.error(request, "Les mots de passe ne sont pas identiques. Veuillez réessayer.")
#             errors = True

#         # Vérification de la sécurité du mot de passe
#         if len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password) or not re.search(r'[!@#$%(),.?\":()|;<>]', password):
#             messages.error(request, "Le mot de passe doit contenir au moins 8 caractères, incluant des lettres, des chiffres et des caractères spéciaux.")
#             errors = True

#         # Validation de l'email
#         try:
#             validate_email(email)
#         except ValidationError:
#             messages.error(request, "L'adresse email est invalide. Veuillez réessayer.")
#             errors = True

#         # Vérification de l'existence du nom d'utilisateur et de l'email
#         # if CustomUser.objects.filter(username=username).exists():
#         #     messages.error(request, "Ce nom d'utilisateur existe déjà. Veuillez en choisir un autre.")
#         #     errors = True

#         if CustomUser.objects.filter(email=email).exists():
#             messages.error(request, "Cet email existe déjà. Veuillez en choisir un autre.")
#             errors = True

#         # Si des erreurs existent, renvoyer le formulaire avec les données valides
#         if errors:
#             return render(request, 'Connexion/create.html', {'form_data': form_data})

#         # Création de l'utilisateur
#         CustomUser.objects.create_user(username=username, first_name=first_name, email=email, password=password)
#         messages.success(request, "Compte créé avec succès. Connectez-vous maintenant.")
#         return redirect('connexion')

#     return render(request, 'shop/creation_compte.html')

# def connexion(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')

#         user = authenticate(email=email, password=password)

#         if user is not None:
#             login(request, user)
#             return redirect('enregistrement')
        
#         else:
#             messages.error(request, "email ou mot de passe incorect")
#             return redirect('connexion')

#     return render(request, 'shop/connexion.html')

# def verification(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
         

#         if not email:
#             messages.error(request, 'veillez entrer une adresse email valide')
#             return redirect('Verification')
        
#         user = CustomUser.objects.filter(email=email).first

#         if user:
#             return redirect('Modification', email=email)
#         else:
#             messages.error(request, 'cette adresse ne correspond a aucun compte')
#             return redirect('Verification')
    
#     return render(request, 'shop/verification_email.html')

# def reset(request, email):
#     try:
#         user = CustomUser.objects.get(email=email)
#     except CustomUser.DoesNotExist:
#         messages.error(request, 'Utilisateur introuvable')
#         return redirect("Verification")
    
#     if request.method == 'POST':
#         password = request.POST.get('password')
#         password_confirm = request.POST.get('password_confirm')

#         if password != password_confirm:

#             messages.error(request, 'Les mots de passe ne correspondent pas. Veuillez réessayer.')
#         else:
#             try:
#                 # Utilise les validateurs intégrés de Django pour vérifier la robustesse du mot de passe
#                 validate_password(password, user=user)
#                 user.set_password(password)
#                 user.save()
#                 messages.success(request, 'Mot de passe modifié avec succès. Connectez-vous maintenant.')
#                 return redirect("connexion")
#             except ValidationError as e:
#                 # Affiche toutes les erreurs de validation
#                 for error in e:
#                     messages.error(request, error)

#     context = {'email': email}

#     return render(request, 'shop/reset.html', {'context': context})


@login_required(login_url='connexion')
def creation(request):
    if request.method == "POST":
        # Récupérer les données du formulaire
        name = request.POST.get("name")
        price = request.POST.get("price")
        category_id = request.POST.get("category")
        smalldescription = request.POST.get("smalldescription")
        description = request.POST.get("description")
        photo = request.FILES.get("photo")  # Récupérer le fichier téléversé
        status = request.POST.get("status")

        # Valider que la catégorie existe
        try:
            category = Category.objects.get(id=category_id)
        except ObjectDoesNotExist:
            messages.error(request, "La catégorie sélectionnée est invalide.")
            return redirect("creation")

        # Créer le produit
        product = Product(
            name=name,
            price=price,
            category=category,
            smalldescription=smalldescription,
            description=description,
            photo=photo,
            status=status
        )
        product.save()  # Sauvegarder dans la base de données

        messages.success(request, "Produit créé avec succès !")
        # return redirect("product_list")  # Redirigez vers la liste des produits (ou une autre page)

    # Si GET, afficher le formulaire
    categories = Category.objects.all()  # Charger les catégories disponibles
    return render(request, 'shop/creation.html', {"categories": categories})

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



@login_required(login_url='connexion')
def commande(request):
    commandes = Commande.objects.all()  # Récupérer toutes les commandes
    context = {
        'commandes': commandes  # Remarquez le changement de nom ici
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