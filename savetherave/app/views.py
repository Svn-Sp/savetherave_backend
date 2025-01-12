import sys

from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
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

from app.models import Party, User
from app.serializer import PartySerializer, UserSerializer


# Create your views here
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def user_info(request, id):
    return JsonResponse(
        UserSerializer(User.objects.get(id=id), context={"request": request}).data
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def token_based_user_info(request):
    return JsonResponse(UserSerializer(request.user, context={"request": request}).data)


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
            {"token": token}, status=status.HTTP_201_CREATED, headers=headers
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def set_profile_picture(request):
    user = request.user
    user.profile_picture = request.FILES.get("image")
    user.save()
    return JsonResponse(UserSerializer(user).data)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_party(request):
    user = request.user
    party = Party.objects.create(
        name=request.data["name"],
        invitation_level=request.data["invitation_level"],
        host=user,
        time=request.data["time"],
        location=request.data["location"],
        image=request.FILES.get("image"),
    )
    party.white_list.add(
        *get_user_model().objects.filter(id__in=request.data["white_list"])
    )
    party.calculate_invited_people()
    party.save()
    return JsonResponse({"party_id": party.id})


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_party_info(request, id):
    party = Party.objects.get(id=id)
    if not party.is_invited(request.user):
        return HttpResponse(status=403)
    return JsonResponse(PartySerializer(party, context={"request": request}).data)
