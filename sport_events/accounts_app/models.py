from django.db import models
from django.contrib.auth.model import AbstractUser

# Create your models here.
class User(AbstractUser):
    class Roles(models.TextChoices):
        ORGANIZER = 'ORGANIZER', 'Организатор'
        PARTICIPANT = 'PARTICIPANT', 'Участник'
    
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.PARTICIPANT
    )

    @property
    def is_organizer(self):
        return self.role == self.Roles.ORGANIZER
