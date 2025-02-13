from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest
from django.db.models import Sum
# import logging

from .models import Product, Category, Commande, DetailCommande, Message, RegimeAlimentaire, Article
import json
from django.contrib.auth.decorators import login_required
from Connexion.models import CustomUser
from django.core.mail import send_mail
from django.conf import settings

from django.utils import timezone

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile


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
        addressli = request.POST.get('addressli')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        total = request.POST.get('total')
        numero_destinataire = request.POST.get('numero_destinataire') or None
        nom_prenom_destinataire = request.POST.get('nom_prenom_destinataire') or None

        # Valider les données du formulaire

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
            user=request.user,
            nom=nom,
            prenom=prenom,
            ville=ville,
            address=address,
            addressli=addressli,
            contact=contact,
            email=email,
            total=total,
            numero_destinataire=numero_destinataire,
            nom_prenom_destinataire=nom_prenom_destinataire,
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

        # Générer le PDF de la commande
        html_content = render_to_string('shop/confirmation.html', {
            'commande': commande,
            'details': commande.details.all()  # Récupérer les détails de la commande
        })

        # Créer la réponse pour le téléchargement du PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="recu_{commande.id}.pdf"'

        # Utiliser WeasyPrint pour générer le PDF
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            HTML(string=html_content).write_pdf(target=temp_file.name)
            response.write(temp_file.read())

        # Retourner le PDF
        return response

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
    categories = Category.objects.all()[1:]

    # Préparer une liste pour stocker les catégories avec leurs produits filtrés
    categories_with_products = []

    for category in categories:
        # Récupérer les produits associés à la catégorie
        produits_in_category = Product.objects.filter(category=category)[:4]

        # Si des produits existent dans cette catégorie après le filtrage, on ajoute la catégorie et ses produits
        if produits_in_category.exists():
            categories_with_products.append({
                'category': category,
                'products': produits_in_category
            })

    # Gestion de la recherche
    query = request.GET.get('item_name')  # Récupère la requête de recherche depuis les paramètres GET
    search_results = []

    if query:
        # Rechercher dans tous les produits selon le nom
        search_results = Product.objects.filter(name__icontains=query)
    return render(request, 'shop/index.html', {'categories_with_products': categories_with_products, 'search_results': search_results, 'query':query })

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
    """Envoie un email pour informer l'utilisateur d'une mise à jour du statut de sa commande."""
    subject = "Mis à jour du statut de votre commande"
    message = f"""Bonjour {commande.nom},

    Le statut de votre commande a été mis à jour.

    Statut actuel : {commande.get_status_display()}.

    Merci de votre confiance à O'VIN CANAN.
    """
    from_email = 'jeaneliseedjelo85@gmail.com'  # Adresse email par défaut
    recipient_list = [commande.email]

    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        # Gestion des erreurs d'envoi d'email (facultatif)
        print(f"Erreur lors de l'envoi de l'email : {e}")


@login_required(login_url='connexion')
def commande(request):
    """Vue pour gérer les commandes et mettre à jour leur statut."""
    commandes = Commande.objects.all()

    if request.method == 'POST':
        commande_id = request.POST.get('commande_id')
        status = request.POST.get('status')

        # Validation du statut
        valid_status = [choice[0] for choice in Commande.STATUS_CHOICES]
        if status not in valid_status:
            messages.error(request, "Statut invalide.")
            return redirect('commande')

        # Récupération de la commande
        commande = get_object_or_404(Commande, id=commande_id)
        previous_status = commande.status
        commande.status = status
        commande.save()

        # Ajout d'un message pour l'utilisateur
        messages.success(request, f"Le statut de la commande {commande.id} a été mis à jour en '{status}'.")

        # Envoi de l'email si le statut a changé
        if previous_status != status:
            send_status_update_email(commande)

        return redirect('commande')

    context = {'commandes': commandes}
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

@login_required
def historique_commande(request):
    if request.user.is_authenticated:
        # Récupérer toutes les commandes passées par l'utilisateur, peu importe l'email utilisé
        commandes = Commande.objects.filter(user=request.user)
    else:
        commandes = Commande.objects.none()  # Aucune commande si pas connecté

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


def recu(request, com_id):
    commande = get_object_or_404(Commande, id=com_id)
    details_commande = commande.details.all()

    context = {'commande': commande, 'details_commande': details_commande}
    return render(request, 'shop/recu.html', context)


def profile(request):
    user = request.user  # Obtenir l'utilisateur actuel
    formatted_join_date = "N/A"  # Valeur par défaut
    formatted_last_login = "N/A"  # Valeur par défaut
    user_nom = "inconnu"
    user_prenom = "inconnu"
    commande_contact = "N/A"  # Valeur par défaut
    commande_ville = "N/A"  # Valeur par défaut

    if user.is_authenticated:
        join_date = user.date_joined  # Obtenir la date d'inscription
        last_login = user.last_login  # Obtenir la dernière connexion

        # Formater la date d'inscription
        if join_date:
            formatted_join_date = join_date.strftime("%B %d, %Y")

        # Formater la dernière connexion
        if last_login:
            time_difference = timezone.now() - last_login
            if time_difference.seconds < 60:
                formatted_last_login = "Il y a quelques secondes"
            elif time_difference.seconds < 3600:
                formatted_last_login = f"Il y a {time_difference.seconds // 60} minutes"
            elif time_difference.days < 1:
                formatted_last_login = f"Il y a {time_difference.seconds // 3600} heures"
            else:
                formatted_last_login = f"{time_difference.days} days ago"

        # Obtenir les informations de l'utilisateur
        user_nom = user.first_name if user.first_name else "inconnu"
        user_prenom = user.username if user.username else "inconnu"

        # Débogage pour afficher l'utilisateur dans les logs
        print(f"Utilisateur connecté : {user}")

        # Récupérer la commande la plus récente associée à l'utilisateur
        commande = Commande.objects.filter(user=user).first()
        if commande:
            print(f"Commande trouvée : {commande}")
            commande_contact = commande.contact
            commande_ville = commande.ville
        else:
            print("Aucune commande trouvée pour cet utilisateur.")

    # Préparer le contexte
    context = {
        'formatted_join_date': formatted_join_date,
        'formatted_last_login': formatted_last_login,
        'user_nom': user_nom,
        'user_prenom': user_prenom,
        'commande_contact': commande_contact,
        'commande_ville': commande_ville,
    }

    return render(request, 'shop/profile.html', context)





@login_required
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        adresse_livraison = request.POST.get('adresse_livraison')
        # Check if the email is taken by other users
        if email and email != user.email and CustomUser.objects.filter(email=email).exists():
             messages.error(request, "Cette adresse email est déjà utilisée par un autre utilisateur.")
             context = {
               'first_name' : first_name if first_name else user.first_name,
               'username' : username if username else user.username,
               'email' : email if email else user.email,
               'contact' : contact if contact else user.contact,
               'adresse_livraison' : adresse_livraison if adresse_livraison else user.adresse_livraison,
             }

        user.first_name = first_name if first_name else user.first_name
        user.username = username if username else user.username
        user.contact = contact if contact else user.contact
        user.adresse_livraison = adresse_livraison if adresse_livraison else user.adresse_livraison
        if email:
            user.email = email
        user.save()
        messages.success(request, 'Profil mis à jour avec succès')
        return redirect('profile')
    context = {
        'first_name' : user.first_name,
        'username' : user.username,
        'email' : user.email,
        'contact' : user.contact,
        'adresse_livraison' : user.adresse_livraison,
    }

    return render(request, 'shop/profile_edit.html', context)


@login_required(login_url='connexion')
def recuCommande(request, recu_id):
    # Récupérer la commande en fonction de l'ID
    commande = get_object_or_404(Commande, id=recu_id)

    # Récupérer les détails associés à cette commande uniquement
    details_commande = DetailCommande.objects.filter(commande=commande)

    # Si le paramètre "pdf" est dans la requête, générer un PDF
    if request.GET.get('pdf'):
        # Rendre le contenu HTML du template pour le PDF
        html_content = render_to_string('shop/reCommande.html', {
            'commande': commande,
            'details_commande': details_commande,
        })

        # Générer le PDF à partir du contenu HTML
        pdf_file = HTML(string=html_content).write_pdf()

        # Créer une réponse HTTP avec le PDF
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="commande_{commande.nom}.pdf"'
        return response

    # Rendre le template HTML classique pour l'affichage
    context = {
        'commande': commande,
        'details_commande': details_commande
    }
    return render(request, 'shop/reCommande.html', context)

def blog(request):
    article_blog = Article.objects.all()
    return render(request, 'shop/blog.html', {'article_blog': article_blog})

def creationar(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        Smalldescription = request.POST.get('Smalldescription', '')
        description = request.POST.get('description', '')
        image = request.FILES.get('image')

        blogs = Article.objects.create(title=title, Smalldescription=Smalldescription, description=description, image=image)
        blogs.save()
    return render(request, 'shop/creationar.html')

def article(request):
    art = Article.objects.all()
    return render(request, 'shop/article.html', {'art': art})

def modif_article(request, art_id):

    get_article = get_object_or_404(Article, id=art_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        Smalldescription = request.POST.get('Smalldescription')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        get_article.title = title
        get_article.Smalldescription = Smalldescription
        get_article.description = description
        if image:
            get_article.image = image

        get_article.save()
        return redirect('article')
    return render(request, 'shop/modif_article.html', {'get_article': get_article})


def blogDetail(request, bd_id):

    blog_article = get_object_or_404(Article, id=bd_id)  # Récupère un seul article ou renvoie 404
    autre_article = Article.objects.exclude(id=bd_id)[:5]  # Exclut l'article en cours et limite à 5


    return render(request, 'shop/blog-detail.html', {'blog_article': blog_article, 'autre_article': autre_article})

def suppresion_art(request, suart_id):
    del_article = get_object_or_404(Article, id=suart_id)
    titles = del_article.title
    if request.method == 'POST':
        del_article.delete()
        return redirect('article')

    return render(request, 'shop/sup_article.html', {'titles': titles})


def propos(request):
    return render(request, 'shop/apropos.html')

def theme(request):
    return render(request, 'shop/theme.html')

