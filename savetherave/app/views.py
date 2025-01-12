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

from app.models import Item, Notification, Party, User
from app.serializer import NotificationSerializer, PartySerializer, UserSerializer


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
def received_requests(request):
    user = request.user
    requests = user.received_requests.all()
    return JsonResponse(
        UserSerializer(requests, many=True, context={"request": request}).data,
        safe=False,
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def are_friends(request):
    id = request.data["id"]
    user = request.user
    if not id:
        return Response({"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        friend = get_user_model().objects.get(id=id)
        are_friends = user.friends.filter(id=friend.id).exists()
        return JsonResponse({"are_friends": are_friends})
    except get_user_model().DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        token, _ = Token.objects.get_or_create(user=serializer.instance)
        return Response(
            {"token": str(token)}, status=status.HTTP_201_CREATED, headers=headers
        )


class AcceptFriendView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserSerializer

    def post(self, request):
        model = get_user_model()
        friend = request.data["id"]
        if not friend:
            return Response(
                {"error": "id who to add is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            friend = model.objects.get(id=friend)
            if friend in request.user.received_requests.all():
                request.user.friends.add(friend)
                request.user.received_requests.remove(friend)
                return Response(
                    {"message": "Friend added successfully"}, status=status.HTTP_200_OK
                )
            return Response(
                {"error": "User sent no request"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except model.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class DeclineFriendView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserSerializer

    def post(self, request):
        model = get_user_model()
        friend = request.data["id"]
        if not friend:
            return Response(
                {"error": "id who to decline is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            friend = model.objects.get(id=friend)
            if friend in request.user.received_requests.all():
                request.user.received_requests.remove(friend)
            else:
                return Response(
                    {"error": "User sent no request"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"message": "Friend declined successfully"}, status=status.HTTP_200_OK
            )
        except model.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class SendRequestView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserSerializer

    def post(self, request):
        model = get_user_model()
        receiver = request.data["id"]
        print("receiver", receiver)
        if not receiver:
            return Response(
                {"error": "id who to send the request is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user_to_request = model.objects.get(id=receiver)
            if user_to_request.friends.filter().exists():
                if request.user in user_to_request.friends.all():
                    return Response(
                        {"error": "user is already a friend"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            user_to_request.received_requests.add(request.user)
            return Response(
                {"message": "Request sent successfully"}, status=status.HTTP_200_OK
            )
        except model.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
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
        spotify_link=request.data.get("spotify_link", None),
        description=request.data.get("description", None),
        max_people=request.data.get("max_people", 9999),
    )
    for item_name, _ in request.data["items"].items():
        item = Item.objects.create(
            name=item_name,
            party=party,
        )
        item.save()
    party.white_list.add(
        *get_user_model().objects.filter(id__in=request.data["white_list"])
    )
    party.calculate_invited_people()
    party.participants.add(user)
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


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_joinable_parties(request):
    user = request.user
    parties = user.allowed_parties.all()
    return JsonResponse(
        PartySerializer(parties, many=True, context={"request": request}).data,
        safe=False,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def assign_to_item(request):
    user = request.user
    item = Item.objects.get(id=request.data["item_id"])
    if not item.party.is_invited(user):
        print("User is not invited")
        return HttpResponse(status=403)
    item.brought_by = user
    item.save()
    return JsonResponse({"message": "Assigned successfully"})


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def join_party(request):
    user = request.user
    party = Party.objects.get(id=request.data["party_id"])
    if not party.is_invited(user):
        return HttpResponse(status=403)
    party.participants.add(user)
    party.save()
    return JsonResponse(
        {
            "message": "Registered successfully",
            "participants": UserSerializer(
                party.participants.all(), many=True, context={"request": request}
            ).data,
        },
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def leave_party(request):
    user = request.user
    party = Party.objects.get(id=request.data["party_id"])
    if not party.is_invited(user):
        return HttpResponse(status=403)
    party.participants.remove(user)
    party.save()
    return JsonResponse(
        {
            "message": "Left successfully",
            "participants": UserSerializer(
                party.participants.all(), many=True, context={"request": request}
            ).data,
        }
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_level_friends(request, level):
    user = request.user
    return JsonResponse(
        UserSerializer(
            user.get_level_friends(level), many=True, context={"request": request}
        ).data,
        safe=False,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def search_users_by_username(request):
    username = request.data["username"]
    if username == "":
        level = 1
        sorted_by_relationship_distance = []
        while level < 5 and len(sorted_by_relationship_distance) < 15:
            friends = request.user.get_level_friends(level)
            for friend in friends:
                if friend in sorted_by_relationship_distance or friend == request.user:
                    continue
                print("Found friend in level", level, friend.username)
                sorted_by_relationship_distance.append(friend)
            level += 1
        return JsonResponse(
            UserSerializer(sorted_by_relationship_distance, many=True).data, safe=False
        )
    users = get_user_model().objects.filter(username__icontains=username)
    return JsonResponse(
        UserSerializer(users, many=True, context={"request": request}).data,
        safe=False,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def notify_party_people(request):
    party = Party.objects.get(id=request.data["party_id"])
    sender = request.user
    notification = Notification.objects.create(
        sender=sender,
        message=request.data["message"],
    )
    if request.data["host_only"]:
        print("Received host only msg", request.data["message"])
        notification.receiver.add(party.host)
    else:
        notification.receiver.add(*party.participants.all())
    notification.save()
    return JsonResponse({"message": "Notified successfully"})


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    user = request.user
    notifications = list(user.received_notifications.all())
    # Delete read notifications
    for notification in notifications:
        notification.delete()
    return JsonResponse(
        NotificationSerializer(
            notifications, many=True, context={"request": request}
        ).data,
        safe=False,
    )

def notify_friend_checked_in(user, party):
    friends = user.friends
    checked_in_friends = friends.filter(checked_into=party)
    notification = Notification.objects.create(
        sender=user,
        message=f"{user.username} has checked into the party {party.name}!",
    )
    for friend in checked_in_friends:
        notification.receiver.add(friend)
    notification.save()

class CheckInView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = PartySerializer

    def post(self, request):
        party_id = request.data["id"]
        joinable_parties = request.user.allowed_parties.all()
        if not joinable_parties.filter(id=party_id).exists():
            return Response(
                {"message": "Forbidden: Non invited"}, status=status.HTTP_403_FORBIDDEN
            )
        model = get_user_model()
        if not party_id:
            return Response(
                {
                    "error": "Party id missing and must be provided with /checkin/<partyid>"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            party = joinable_parties.get(id=party_id)
            if (
                party.checked_in.exists()
                and party.checked_in.filter(id=request.user.id).exists()
            ):
                return Response(
                    {"error": "User is already checked in."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if party.invited_people.filter(id=request.user.id).exists():
                party.checked_in.add(request.user)
                notify_friend_checked_in(request.user, party)
                return Response(
                    {"message": "Successfully checked in."}, status=status.HTTP_200_OK
                )
            return Response(
                {"message": "Forbidden: Non invited"}, status=status.HTTP_403_FORBIDDEN
            )
        except model.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
