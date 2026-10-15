from django.db import models

# Create your models here.

class Event(models.Model):
    

class Event_Sign_Up(models.Model):

class Event_Results(models.Model):



class Event(models.Model):
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_events",
        verbose_name="Организатор",
    )
    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True)
    date = models.DateField("Дата проведения")
    location = models.CharField("Место проведения", max_length=200)

    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"

    def __str__(self):
        return self.title


class Registration(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Подтверждено"
        CANCELLED = "cancelled", "Отменено"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name="Участник",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name="Мероприятие",
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )
    created_at = models.DateTimeField("Дата регистрации", auto_now_add=True)

    class Meta:
        verbose_name = "Регистрация на мероприятие"
        verbose_name_plural = "Регистрации на мероприятия"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "event"],
                name="unique_user_event_registration",
            ),
        ]

    def __str__(self):
        return f"{self.user} — {self.event} ({self.get_status_display()})"


class Result(models.Model):
    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        related_name="result",
        verbose_name="Регистрация",
    )
    time = models.CharField("Время", max_length=50, blank=True)
    place = models.PositiveIntegerField("Место", null=True, blank=True)
    points = models.PositiveIntegerField("Баллы", null=True, blank=True)

    class Meta:
        verbose_name = "Результат"
        verbose_name_plural = "Результаты"

    def __str__(self):
        return f"Результат: {self.registration}"



