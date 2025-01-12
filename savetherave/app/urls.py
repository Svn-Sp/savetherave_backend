from django.conf.urls.static import static
from django.urls import include, path
from django.views.static import serve

from app import views
from savetherave import settings

urlpatterns = [
    # path("user/friends_info", views.friends_info),
    path("user/<int:id>", views.user_info),
    path("user/create", views.CreateUserView.as_view()),
    path("user/set_profile_picture", views.set_profile_picture),
    path("user/add_friend", views.AddFriendView.as_view()),
    path("party/create", views.create_party),
    path("party/<int:id>", views.get_party_info),
]
