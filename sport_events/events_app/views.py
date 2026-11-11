from django.shortcuts import render
from .models import Event

def home(request):
	events = Event.objects.select_related("organizer").order_by("date")
	return render(request, "home.html", {"events": events})
