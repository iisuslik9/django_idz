from django.urls import path
from . import views

urlpatterns = [
    path("register/participant/", views.register_participant, name="register_participant"),
    path("register/organizer/", views.register_organizer, name="register_organizer"),
    path("organizer-pending/", views.organizer_pending, name="organizer_pending"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"),
]
