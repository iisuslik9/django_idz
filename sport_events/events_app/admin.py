from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Organizer, Participant, Event, Registration, EventResult, Feedback


@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone")


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("full_name", "birth_date", "city")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "organizer", "date", "location")
    list_filter = ("date",)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("participant", "event", "status", "created_at")
    list_filter = ("status", "event")


@admin.register(EventResult)
class EventResultAdmin(admin.ModelAdmin):
    list_display = ("registration", "place", "finish_time", "score")

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("author_name", "event", "email", "created_at")
    list_filter = ("event",)

