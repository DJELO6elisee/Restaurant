from django.urls import path
from .views import create, connexion, verification, reset, deconnexion


urlpatterns = [
    path('create/', create, name='create'),
    path('connexion/', connexion, name='connexion'),
    path('verification/', verification, name='verification'),
    path('reset/<str:email>/', reset, name='reset'),
    path('deconnexion/', deconnexion, name='deconnexion'),
    
]