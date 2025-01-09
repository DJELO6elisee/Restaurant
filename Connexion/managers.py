from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        """
        Créer et retourner un utilisateur avec un email et un mot de passe.
        """
        if not email:
            raise ValueError('L\'email doit être renseigné')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Créer et retourner un superutilisateur avec un email et un mot de passe.
        """
        # Assurer que ces valeurs sont définies
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Vérifie la présence du username et email
        if not username:
            raise ValueError('Le nom d\'utilisateur doit être renseigné')
        if not email:
            raise ValueError('L\'email doit être renseigné')

        return self.create_user(email, username, password, **extra_fields)
