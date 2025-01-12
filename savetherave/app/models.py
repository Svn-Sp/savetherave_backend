# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver


class User(AbstractUser):
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    birthday = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    phone_number = models.CharField(max_length=25, blank=True, null=True)
    received_requests = models.ManyToManyField(
        "self", blank=True, symmetrical=False)
    friends = models.ManyToManyField("self", blank=True)
    instagram = models.CharField(max_length=99, blank=True, null=True)

    def get_level_friends(self, level: int) -> list["User"]:
        if level < 1:
            raise ValueError("Level must be greater than 0")
        friends = []
        visited_ids = set()
        multilevel_queue = [[friend for friend in self.friends.all()]]
        while len(multilevel_queue) <= level:
            multilevel_queue.append([])
            for friend in multilevel_queue[-2]:
                if friend.id in visited_ids or friend == self:
                    continue
                visited_ids.add(friend.id)
                friends.append(friend)
                multilevel_queue[-1].extend(friend.friends.all())
        return friends


class Party(models.Model):
    name = models.CharField(max_length=100)
    invitation_level = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    spotify_link = models.CharField(max_length=100, blank=True, null=True)
    host = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_parties"
    )
    time = models.DateTimeField()
    location = models.CharField(max_length=100)
    image = models.ImageField(upload_to="party_images/", blank=True, null=True)
    participants = models.ManyToManyField(
        User, blank=True)  # User who announced to come
    checked_in = models.ManyToManyField(
        User, blank=True, related_name="checked_into")  # User who are already checked in
    white_list = models.ManyToManyField(
        User, blank=True, related_name="white_lists")
    invited_people = models.ManyToManyField(
        User, blank=True, related_name="allowed_parties"
    )  # all Users who may come

    def __str__(self):
        return self.name

    def calculate_invited_people(self) -> list[User]:
        self.invited_people.add(*self.white_list.all())
        self.invited_people.add(
            *self.host.get_level_friends(self.invitation_level))
        self.save()

    # todo THIS DOES NOT WORK
    # @receiver(m2m_changed, sender=User.friends.through)
    # def update_invited_people(sender, instance, action, **kwargs):
    #     if action in ["post_add", "post_remove"]:
    #         for party in instance.owned_parties.all():
    #             party.invited_people.clear()
    #             party.calculate_invited_people()

    # m2m_changed.connect(update_invited_people, sender=User.friends.through)


    def is_invited(self, user: User) -> bool:
        return user in self.invited_people.all() or user == self.host


class Item(models.Model):
    name = models.CharField(max_length=100)
    brought_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="items")


class Notification(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_notifications"
    )
    receiver = models.ManyToManyField(User, related_name="received_notifications")
    message = models.TextField()
