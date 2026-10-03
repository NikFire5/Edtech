from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Студент'
        INSTRUCTOR = 'INSTRUCTOR', 'Преподаватель'
        ADMIN = 'ADMIN', 'Администратор'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name='Роль'
    )
    bio = models.TextField('О себе', blank=True)

    def is_admin(self) -> bool:
        """Администратор сайта: управляет любыми курсами, уроками и категориями."""
        return self.role == self.Role.ADMIN or self.is_superuser

    def is_instructor(self) -> bool:
        """Может создавать курсы: преподаватели и администраторы."""
        return self.role in (self.Role.INSTRUCTOR, self.Role.ADMIN) or self.is_superuser

    def is_student(self) -> bool:
        return self.role == self.Role.STUDENT

    def display_name(self) -> str:
        return self.get_full_name() or self.username

    def __str__(self) -> str:
        return f"{self.username} ({self.get_role_display()})"
