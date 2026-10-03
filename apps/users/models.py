from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Студент'
        INSTRUCTOR = 'INSTRUCTOR', 'Преподаватель'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name='Роль'
    )
    bio = models.TextField('О себе', blank=True)

    def is_instructor(self) -> bool:
        return self.role == self.Role.INSTRUCTOR or self.is_superuser

    def is_student(self) -> bool:
        return self.role == self.Role.STUDENT

    def __str__(self) -> str:
        return f"{self.username} ({self.get_role_display()})"