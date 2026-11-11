from django.db import models

# Create your models here.

class Organizer(models.Model):
    full_name = models.CharField(max_length=200, verbose_name="ФИО / Название организации")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Контактный телефон")

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Организатор"
        verbose_name_plural = "Организаторы"


class Participant(models.Model):
    full_name = models.CharField(max_length=200, verbose_name="ФИО участника")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Участник"
        verbose_name_plural = "Участники"


class Event(models.Model):
    organizer = models.ForeignKey(
        Organizer,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name="Организатор",
    )
    title = models.CharField(max_length=200, verbose_name="Название мероприятия")
    description = models.TextField(verbose_name="Описание")
    date = models.DateTimeField(verbose_name="Дата и время проведения")
    location = models.CharField(max_length=255, verbose_name="Место проведения")

    def __str__(self):
        return f"{self.title} ({self.date.strftime('%d.%m.%Y')})"

    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"
        ordering = ["date"]


class Registration(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Подтверждено"
        CANCELLED = "cancelled", "Отменено"

    participant = models.ForeignKey(
        Participant,
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
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
        verbose_name="Статус",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")

    def __str__(self):
        return f"{self.participant.full_name} — {self.event.title} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Регистрация на мероприятие"
        verbose_name_plural = "Регистрации на мероприятия"
        unique_together = ("participant", "event")


class EventResult(models.Model):
    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        related_name="result",
        verbose_name="Регистрация участника",
    )
    finish_time = models.DurationField(
        null=True,
        blank=True,
        verbose_name="Время (чч:мм:сс)",
    )
    place = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Занятое место",
    )
    score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Баллы",
    )

    def __str__(self):
        return f"Результат: {self.registration.participant.full_name} ({self.registration.event.title})"

    class Meta:
        verbose_name = "Результат мероприятия"
        verbose_name_plural = "Результаты мероприятий"
        ordering = ["place", "-score"]



