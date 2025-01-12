from django.conf.urls.static import static
from django.urls import include, path
from django.views.static import serve

from app import views
from savetherave import settings

urlpatterns = [
    path("user/", views.user_info),
    path("user/create", views.CreateUserView.as_view()),
    path("user/set_profile_picture", views.set_profile_picture),
    path("party/create", views.create_party),
    path("party/<int:pk>", views.get_party_info),
]
