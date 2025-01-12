from __future__ import annotations

from django.contrib.auth import get_user_model
from django.urls import include, path
from rest_framework import routers, serializers, status, viewsets

from app.models import Item, Party


class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True)
    profile_picture_link = serializers.SerializerMethodField()
    friends = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    received_requests = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    def get_profile_picture_link(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        return None

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "password",
            "birthday",
            "gender",
            "phone_number",
            "received_requests",
            "friends",
            "instagram",
            "profile_picture_link",
        ]


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    brought_by = UserSerializer()

    class Meta:
        model = Item
        fields = ["id", "name", "brought_by"]


class PartySerializer(serializers.HyperlinkedModelSerializer):
    host = UserSerializer()
    participants = UserSerializer(many=True)
    checked_in = UserSerializer(many=True)
    image_link = serializers.SerializerMethodField()
    items = ItemSerializer(many=True)

    def get_image_link(self, obj):
        if obj.image:
            return obj.image.url
        return None

    class Meta:
        model = Party
        fields = [
            "id",
            "name",
            "invitation_level",
            "items",
            "description",
            "spotify_link",
            "host",
            "time",
            "location",
            "image_link",
            "participants",
            "checked_in"
        ]
