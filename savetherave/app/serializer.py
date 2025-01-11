from django.contrib.auth import get_user_model
from django.urls import include, path
from rest_framework import routers, serializers, status, viewsets


class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True)
    profile_picture_link = serializers.SerializerMethodField()

    def get_profile_picture_link(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        return None

    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "password",
            "birthday",
            "gender",
            "phone_number",
            "friends",
            "instagram_url",
            "profile_picture_link",
        ]
