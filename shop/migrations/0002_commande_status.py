# Generated by Django 5.1.4 on 2024-12-26 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='commande',
            name='status',
            field=models.CharField(choices=[('pending', 'En attente'), ('processing', 'En cours de traitement'), ('shipped', 'Expédiée'), ('delivered', 'Livrée')], default='pending', max_length=20),
        ),
    ]
