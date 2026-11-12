from django import forms
from django.contrib.auth.forms import UserCreationForm

from events_app.models import Participant, Organizer
from .models import User


class ParticipantRegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    full_name = forms.CharField(
        max_length=200,
        label="ФИО участника",
    )
    birth_date = forms.DateField(
        required=False,
        label="Дата рождения",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        label="Город",
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "full_name",
            "birth_date",
            "city",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = User.Role.PARTICIPANT
        user.is_approved = True

        if commit:
            participant = Participant.objects.create(
                full_name=self.cleaned_data["full_name"],
                birth_date=self.cleaned_data.get("birth_date"),
                city=self.cleaned_data.get("city", ""),
            )
            user.participant = participant
            user.save()

        return user


class OrganizerRegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    full_name = forms.CharField(
        max_length=200,
        label="ФИО / Название организации",
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label="Контактный телефон",
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "full_name",
            "phone",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = User.Role.ORGANIZER
        user.is_approved = False

        if commit:
            organizer = Organizer.objects.create(
                full_name=self.cleaned_data["full_name"],
                phone=self.cleaned_data.get("phone", ""),
            )
            user.organizer = organizer
            user.save()

        return user

class ProfileEditForm(forms.ModelForm):
    full_name = forms.CharField(max_length=200, label="ФИО / Название организации")

    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.role == User.Role.PARTICIPANT and self.instance.participant:
            self.fields["full_name"].initial = self.instance.participant.full_name
        elif self.instance.role == User.Role.ORGANIZER and self.instance.organizer:
            self.fields["full_name"].initial = self.instance.organizer.full_name

    def save(self, commit=True):
        user = super().save(commit=commit)
        full_name = self.cleaned_data["full_name"]
        if user.role == User.Role.PARTICIPANT and user.participant:
            user.participant.full_name = full_name
            user.participant.save()
        elif user.role == User.Role.ORGANIZER and user.organizer:
            user.organizer.full_name = full_name
            user.organizer.save()
        return user
