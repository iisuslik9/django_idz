from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from accounts_app.models import User
from django.conf import settings
from django.core.mail import send_mail
from .forms import EventForm, EventResultForm, EventRegistrationForm, FeedbackForm
from .models import Event, Registration, EventResult, Feedback

def home(request):
    events = Event.objects.all()
    # Фильтрация по дате, месту проведения и типу мероприятия
    date_query = request.GET.get("date")
    location_query = request.GET.get("location")
    type_query = request.GET.get("event_type")

    if date_query:
        events = events.filter(date__date=date_query)
    if location_query:
        events = events.filter(location__icontains=location_query)
    if type_query:
        events = events.filter(event_type=type_query)

    return render(
        request,
        "events_app/home.html",
        {
            "events": events,
            "event_types": Event.EventType.choices,
            "selected_date": date_query or "",
            "selected_location": location_query or "",
            "selected_type": type_query or "",
        },
    )


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user_registration = None

    if request.user.is_authenticated and request.user.role == User.Role.PARTICIPANT:
        user_registration = Registration.objects.filter(
            participant=request.user.participant,
            event=event,
        ).first()

    if request.method == "POST":
        feedback_form = FeedbackForm(request.POST)
        if feedback_form.is_valid():
            feedback = feedback_form.save(commit=False)
            feedback.event = event  # привязываем к текущему мероприятию
            feedback.save()
            messages.success(request, "Ваш отзыв добавлен")
            return redirect("event_detail", event_id=event.id)
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data["email"] = request.user.email
            if request.user.role == User.Role.PARTICIPANT and request.user.participant:
                initial_data["author_name"] = request.user.participant.full_name
        feedback_form = FeedbackForm(initial=initial_data)

    feedbacks = event.feedbacks.all().order_by("-created_at")

    return render(
        request,
        "events_app/event_details.html",
        {
            "event": event,
            "user_registration": user_registration,
            "feedback_form": feedback_form,
            "feedbacks": feedbacks,
        },
    )


# @login_required
# def register_for_event(request, event_id):
#     if request.user.role != User.Role.PARTICIPANT:
#         messages.error(request, "Регистрироваться на мероприятия могут только участники")
#         return redirect("event_detail", event_id=event_id)

#     event = get_object_or_404(Event, id=event_id)
#     registration, created = Registration.objects.get_or_create(
#         participant=request.user.participant,
#         event=event,
#         defaults={"status": Registration.Status.CONFIRMED},
#     )

#     if not created and registration.status == Registration.Status.CANCELLED:
#         registration.status = Registration.Status.CONFIRMED
#         registration.save()

#     return redirect("participant_cabinet")
@login_required
def register_for_event(request, event_id):
    if request.user.role != User.Role.PARTICIPANT:
        messages.error(request, "Регистрироваться на мероприятия могут только участники")
        return redirect("event_detail", event_id=event_id)

    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            registration, created = Registration.objects.get_or_create(
                participant=request.user.participant,
                event=event,
                defaults={"status": Registration.Status.CONFIRMED},
            )
            if not created and registration.status == Registration.Status.CANCELLED:
                registration.status = Registration.Status.CONFIRMED
                registration.save()

            # Отправка email-уведомления о подтверждении регистрации
            if request.user.email:
                send_mail(
                    subject=f"Подтверждение регистрации: {event.title}",
                    message=(
                        f"Здравствуйте, {request.user.participant.full_name}!\n"
                        f"Вы успешно зарегистрированы на мероприятие «{event.title}».\n"
                        f"Дата: {event.date.strftime('%d.%m.%Y %H:%M')}, Место: {event.location}."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )
            return redirect("participant_cabinet")
    else:
        form = EventRegistrationForm()

    return render(
        request,
        "events_app/register_event.html",
        {"form": form, "event": event},
    )


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
        "events_app/participant_cabinet.html",
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
        "events_app/organizer_cabinet.html",
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

    return render(request, "events_app/create_event.html", {"form": form})


@login_required
def manage_event(request, event_id):
    if request.user.role != User.Role.ORGANIZER:
        return redirect("home")

    event = get_object_or_404(Event, id=event_id, organizer=request.user.organizer)
    registrations = event.registrations.select_related("participant", "result")
    feedbacks = event.feedbacks.all().order_by("-created_at")

    return render(
        request,
        "events_app/manage_event.html",
        {
            "event": event,
            "registrations": registrations,
            "feedbacks": feedbacks,
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

            # Отправка email-уведомления с результатами участнику
            participant_user = getattr(registration.participant, "user_account", None)
            if participant_user and participant_user.email:
                send_mail(
                    subject=f"Результаты мероприятия: {registration.event.title}",
                    message=(
                        f"Здравствуйте, {registration.participant.full_name}!\n"
                        f"Опубликованы ваши результаты по мероприятию «{registration.event.title}»:\n"
                        f"Место: {new_result.place or '—'}\n"
                        f"Время: {new_result.finish_time or '—'}\n"
                        f"Баллы: {new_result.score or '—'}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[participant_user.email],
                    fail_silently=True,
                )
            return redirect("manage_event", event_id=registration.event.id)
    else:
        form = EventResultForm(instance=result)

    return render(
        request,
        "events_app/add_result.html",
        {"form": form, "registration": registration},
    )


def feedback_view(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Спасибо! Ваш отзыв успешно отправлен.")
            return redirect("home")
    else:
        form = FeedbackForm()

    return render(request, "events_app/feedback.html", {"form": form})