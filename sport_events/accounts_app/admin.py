from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
# Register your models here.


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "role",
        "participant",
        "organizer",
        "is_approved",
        "is_staff",
    )

    list_filter = ("role", "is_approved", "is_staff")

    search_fields = (
        "username",
        "email",
        "participant__full_name",
        "organizer__full_name",
    )

    list_editable = ("is_approved",)

    fieldsets = UserAdmin.fieldsets + (
        (
            "Профиль и роль",
            {
                "fields": (
                    "role",
                    "participant",
                    "organizer",
                    "is_approved",
                )
            },
        ),
    )
