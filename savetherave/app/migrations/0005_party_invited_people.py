# Generated by Django 5.1.4 on 2025-01-12 02:41

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_party_white_list'),
    ]

    operations = [
        migrations.AddField(
            model_name='party',
            name='invited_people',
            field=models.ManyToManyField(blank=True, related_name='allowed_parties', to=settings.AUTH_USER_MODEL),
        ),
    ]