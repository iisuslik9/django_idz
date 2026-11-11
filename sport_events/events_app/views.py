from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from accounts_app.models import User
from .forms import EventForm, EventResultForm
from .models import Event, Registration, EventResult


def home(request):
    events = Event.objects.all()
    return render(request, "events/home.html", {"events": events})


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user_registration = None

    if request.user.is_authenticated and request.user.role == User.Role.PARTICIPANT:
        user_registration = Registration.objects.filter(
            participant=request.user.participant,
            event=event,
        ).first()

    return render(
        request,
        "events/event_detail.html",
        {
            "event": event,
            "user_registration": user_registration,
        },
    )


@login_required
def register_for_event(request, event_id):
    if request.user.role != User.Role.PARTICIPANT:
        messages.error(request, "Регистрироваться на мероприятия могут только участники.")
        return redirect("event_detail", event_id=event_id)

    event = get_object_or_404(Event, id=event_id)
    registration, created = Registration.objects.get_or_create(
        participant=request.user.participant,
        event=event,
        defaults={"status": Registration.Status.CONFIRMED},
    )

    if not created and registration.status == Registration.Status.CANCELLED:
        registration.status = Registration.Status.CONFIRMED
        registration.save()

    return redirect("participant_cabinet")


@login_required
def cancel_registration(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id)

    is_owner = (
        request.user.role == User.Role.PARTICIPANT
        and registration.participant == request.user.participant
    )
    is_event_organizer = (
        request.user.role == User.Role.ORGANIZER
        and registration.event.organizer == request.user.organizer
    )

    if is_owner or is_event_organizer:
        registration.status = Registration.Status.CANCELLED
        registration.save()

    if is_event_organizer:
        return redirect("manage_event", event_id=registration.event.id)
    return redirect("participant_cabinet")


@login_required
def participant_cabinet(request):
    if request.user.role != User.Role.PARTICIPANT:
        return redirect("home")

    now = timezone.now()
    registrations = Registration.objects.filter(
        participant=request.user.participant
    ).select_related("event", "result")

    upcoming_registrations = registrations.filter(event__date__gte=now)
    past_registrations = registrations.filter(event__date__lt=now)

    return render(
        request,
        "events/participant_cabinet.html",
        {
            "upcoming_registrations": upcoming_registrations,
            "past_registrations": past_registrations,
        },
    )


@login_required
def organizer_cabinet(request):
    if request.user.role != User.Role.ORGANIZER:
        return redirect("home")

    events = Event.objects.filter(organizer=request.user.organizer)
    return render(
        request,
        "events/organizer_cabinet.html",
        {"events": events},
    )


@login_required
def create_event(request):
    if request.user.role != User.Role.ORGANIZER:
        return redirect("home")

    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user.organizer
            event.save()
            return redirect("organizer_cabinet")
    else:
        form = EventForm()

    return render(request, "events/create_event.html", {"form": form})


@login_required
def manage_event(request, event_id):
    if request.user.role != User.Role.ORGANIZER:
        return redirect("home")

    event = get_object_or_404(Event, id=event_id, organizer=request.user.organizer)
    registrations = event.registrations.select_related("participant", "result")

    return render(
        request,
        "events/manage_event.html",
        {
            "event": event,
            "registrations": registrations,
        },
    )


@login_required
def add_or_edit_result(request, registration_id):
    if request.user.role != User.Role.ORGANIZER:
        return redirect("home")

    registration = get_object_or_404(
        Registration,
        id=registration_id,
        event__organizer=request.user.organizer,
    )
    result = getattr(registration, "result", None)

    if request.method == "POST":
        form = EventResultForm(request.POST, instance=result)
        if form.is_valid():
            new_result = form.save(commit=False)
            new_result.registration = registration
            new_result.save()
            return redirect("manage_event", event_id=registration.event.id)
    else:
        form = EventResultForm(instance=result)

    return render(
        request,
        "events/add_result.html",
        {
            "form": form,
            "registration": registration,
        },
    )

