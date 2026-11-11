from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        ORGANIZER = "organizer", "Организатор"
        PARTICIPANT = "participant", "Участник"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PARTICIPANT,
        verbose_name="Роль",
    )

    organizer = models.OneToOneField(
        "events_app.Organizer",
        on_delete=models.PROTECT,  # защищаем созданные мероприятия от удаления при удалении аккаунта
        null=True,
        blank=True,
        related_name="user_account",
        verbose_name="Карточка организатора",
    )

    participant = models.OneToOneField(
        "events_app.Participant",
        on_delete=models.PROTECT,  # защищаем историю участий и результатов от каскадного удаления
        null=True,
        blank=True,
        related_name="user_account",
        verbose_name="Карточка участника",
    )

    is_approved = models.BooleanField(
        default=False,
        verbose_name="Подтвержден администратором",
    )

    def __str__(self):
        return f"{self.username} — {self.get_role_display()}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
