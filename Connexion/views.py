from django.shortcuts import render, redirect
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.password_validation import validate_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import CustomUser

def create(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire avec .get()
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        adresse = request.POST.get('adresse')
        adresse_livraison = request.POST.get('adresse_livraison')

        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # Stocker les valeurs valides dans un dictionnaire pour les réutiliser
        form_data = {
            'username': username,
            'first_name': first_name,
            'email': email,
            'contact': contact,
            'adresse': adresse,
            'adresse_livraison': adresse_livraison,
        }

        # Initialiser une variable pour suivre les erreurs
        errors = False

        # Vérifier si tous les champs sont remplis
        if not username or not first_name or not email or not password or not password_confirm:
            messages.error(request, "Tous les champs doivent être remplis.")
            errors = True

        # Vérifier si les mots de passe sont identiques
        if password != password_confirm:
            messages.error(request, "Les mots de passe ne sont pas identiques. Veuillez réessayer.")
            errors = True

        # Vérification de la sécurité du mot de passe
        if len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password) or not re.search(r'[!@#$%(),.?\":()|;<>]', password):
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères, incluant des lettres, des chiffres et des caractères spéciaux.")
            errors = True

        # Validation de l'email
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "L'adresse email est invalide. Veuillez réessayer.")
            errors = True

        # Vérification de l'existence du nom d'utilisateur et de l'email
        # if CustomUser.objects.filter(username=username).exists():
        #     messages.error(request, "Ce nom d'utilisateur existe déjà. Veuillez en choisir un autre.")
        #     errors = True

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Cet email existe déjà. Veuillez en choisir un autre.")
            errors = True

        # Si des erreurs existent, renvoyer le formulaire avec les données valides
        if errors:
            return render(request, 'Connexion/creation_compte.html', {'form_data': form_data})

        # Création de l'utilisateur
        CustomUser.objects.create_user(username=username, first_name=first_name, email=email, contact=contact, adresse=adresse, adresse_livraison=adresse_livraison, password=password)
        messages.success(request, "Compte créé avec succès. Connectez-vous maintenant.")
        return redirect('connexion')

    return render(request, 'Connexion/creation_compte.html')

def create_superuser():
    """
    Fonction pour créer un superutilisateur si aucun n'existe.
    """
    # Créer un superutilisateur dans la base de données
    if not CustomUser.objects.filter(email='kuyo@gmail.com').exists():
        CustomUser.objects.create_superuser(email='kuyo@gmail.com', username='kuyo', password='123abc!@#')
        print("Superutilisateur créé.")

def connexion(request):
    # Créer un superutilisateur si nécessaire
    create_superuser()

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authentification de l'utilisateur
        # Modifiez ici si vous authentifiez avec email
        user = authenticate(request, email=email, password=password)  # Utilisez 'username' ou ajustez la méthode

        if user is not None:
            login(request, user)  # Connexion de l'utilisateur

            # if user.is_superuser:  # Vérifie si l'utilisateur est un superutilisateur
            #     return redirect('adminp')  # Redirige vers la page admin Django

            # Vérifier si l'utilisateur est un superutilisateur
            if user.is_staff:  # Vérifie si l'utilisateur est un superutilisateur
                return redirect('adminp')  # Redirige vers la page admin Django

            # Vous pouvez ajouter une redirection vers une page normale si l'utilisateur n'est pas un superutilisateur
            return redirect('shop')  # Par exemple vers la page d'accueil

        else:
            messages.error(request, "Email ou mot de passe incorrect")
            return redirect('connexion')  # Rediriger vers la page de connexion en cas d'erreur

    return render(request, 'Connexion/connexion.html')


def verification(request):
    if request.method == 'POST':
        email = request.POST.get('email')


        if not email:
            messages.error(request, 'veillez entrer une adresse email valide')
            return redirect('verification')

        user = CustomUser.objects.filter(email=email).first

        if user:
            return redirect('reset', email=email)
        else:
            messages.error(request, 'cette adresse ne correspond a aucun compte')
            return redirect('verification')

    return render(request, 'Connexion/verification_email.html')


def reset(request, email):
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Utilisateur introuvable')
        return redirect("verification")

    if request.method == 'POST':
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:

            messages.error(request, 'Les mots de passe ne correspondent pas. Veuillez réessayer.')
        else:
            try:
                # Utilise les validateurs intégrés de Django pour vérifier la robustesse du mot de passe
                validate_password(password, user=user)
                user.set_password(password)
                user.save()
                messages.success(request, 'Mot de passe modifié avec succès. Connectez-vous maintenant.')
                return redirect("connexion")
            except ValidationError as e:
                # Affiche toutes les erreurs de validation
                for error in e:
                    messages.error(request, error)

    context = {'email': email}

    return render(request, 'Connexion/reset.html', {'context': context})

def deconnexion(request):
        logout(request)
        messages.success(request, 'Utilisateur deconnecter avec succes')
        return redirect('connexion')

