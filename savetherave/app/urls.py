from django.conf.urls.static import static
from django.urls import include, path
from django.views.static import serve

from app import views
from savetherave import settings

urlpatterns = [
    path("user/<int:id>/", views.user_info),
    path("user/send_request/", views.SendRequestView.as_view()),
    path("user/received_requests/", views.received_requests),
    path("user/create/", views.CreateUserView.as_view()),
    path("user/set_profile_picture/", views.set_profile_picture),
    path("user/are_friends/", views.are_friends),
    path("user/accept/", views.AcceptFriendView.as_view()),
    path("user/decline/", views.DeclineFriendView.as_view()),
    path("party/create/", views.create_party),
    path("party/<int:id>/", views.get_party_info),
    path("user/", views.token_based_user_info),
    path("party/relevants/", views.get_relevant_parties),
    path("item/assign/", views.assign_to_item),
    path("party/checkin/", views.CheckInView.as_view()),
    path("party/join/", views.join_party),
    path("party/leave/", views.leave_party),
    path("user/level_friends/", views.get_level_friends),
    path("user/search/", views.search_users_by_username),
    path("party/notify/", views.notify_party_people),
    path("user/notifications/", views.get_notifications),
    path("user/report/", views.report_guest),
    path("bringbackbuddy/request/", views.request_bring_back_buddy),
    path("bringbackbuddy/", views.get_bring_back_buddy_requests),
    path("bringbackbuddy/apply/", views.apply_as_bring_back_buddy),
    path("user/last_check_in/", views.get_latest_check_in),
    path("bringbackbuddy/review/", views.review_buddy_application),
]
