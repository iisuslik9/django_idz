from django import forms
from .models import Event, EventResult


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ("title", "description", "date", "location")
        widgets = {
            "date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class EventResultForm(forms.ModelForm):
    class Meta:
        model = EventResult
        fields = ("finish_time", "place", "score")
        widgets = {
            "finish_time": forms.TextInput(attrs={"placeholder": "01:25:30"}),
        }
