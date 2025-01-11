# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    birthday = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    friends = models.ManyToManyField("self", blank=True)
    instagram_url = models.URLField(blank=True, null=True)


class Party(models.Model):
    name = models.CharField(max_length=100)
    invitation_level = models.IntegerField()
    host = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_parties"
    )
    time = models.DateTimeField()
    location = models.CharField(max_length=100)
    image = models.ImageField(upload_to="party_images/", blank=True, null=True)
    participants = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name
