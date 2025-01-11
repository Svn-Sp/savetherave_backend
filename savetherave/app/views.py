from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from app.serializer import UserSerializer


# Create your views here
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_info(request):
    return JsonResponse(UserSerializer(request.user).data)


class CreateUserView(CreateAPIView):
    model = get_user_model()
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):  # <- here i forgot self
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        token, _ = Token.objects.get_or_create(user=serializer.instance)
        return Response(
            {"token": token.key}, status=status.HTTP_201_CREATED, headers=headers
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def set_profile_picture(request):
    user = request.user
    user.profile_picture = request.FILES.get("image")
    user.save()
    return JsonResponse(UserSerializer(user).data)
