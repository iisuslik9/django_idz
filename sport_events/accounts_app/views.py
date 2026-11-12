from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect

from .forms import (
    ParticipantRegistrationForm,
    OrganizerRegistrationForm,
)
from .models import User


def register_participant(request):
    if request.method == "POST":
        form = ParticipantRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = ParticipantRegistrationForm()

    return render(
        request,
        "accounts_app/register_participant.html",
        {"form": form},
    )


def register_organizer(request):
    if request.method == "POST":
        form = OrganizerRegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("organizer_pending")
    else:
        form = OrganizerRegistrationForm()

    return render(
        request,
        "accounts_app/register_organizer.html",
        {"form": form},
    )


def organizer_pending(request):
    return render(
        request,
        "accounts_app/organizer_pending.html",
    )


class UserLoginView(LoginView):
    template_name = "accounts_app/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        # если вошел организатор, но админ его еще не подтвердил
        if user.role == User.Role.ORGANIZER and not user.is_approved:
            logout(self.request)
            return redirect("organizer_pending")
        return response


class UserLogoutView(LogoutView):
    next_page = "login"


@login_required
def profile(request):
    return render(
        request,
        "accounts_app/profile.html",
        {"profile": request.user},
    )
