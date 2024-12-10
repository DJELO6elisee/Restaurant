from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        if email is None:
            return None
        try:
            # Chercher l'utilisateur par email
            user = get_user_model().objects.get(email=email)
            # Vérifier le mot de passe
            if user.check_password(password):
                return user
            return None
        except get_user_model().DoesNotExist:
            return None
