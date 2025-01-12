from django.conf.urls.static import static
from django.urls import include, path
from django.views.static import serve

from app import views
from savetherave import settings

urlpatterns = [
    path("user/<int:id>", views.user_info),
    path("user/send_request", views.SendRequestView.as_view()),
    path("user/received_requests", views.received_requests),
    path("user/create", views.CreateUserView.as_view()),
    path("user/set_profile_picture", views.set_profile_picture),
    path("user/are_friends", views.are_friends),
    path("user/accept", views.AcceptFriendView.as_view()),
    path("user/decline", views.DeclineFriendView.as_view()),
    path("party/create", views.create_party),
    path("party/<int:id>", views.get_party_info),
    path("user/", views.token_based_user_info),
    path("user/add_friend/", views.AddFriendView.as_view()),
    path("party/joinables/", views.get_joinable_parties),
    path("item/assign/", views.assign_to_item),
    path("party/join/", views.join_party),
    path("party/leave/", views.leave_party),
]
