from django.db import models
from django.contrib.auth.models import AbstractUser

class Client(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        ANALYST = 'ANALYST', 'Analyst'
        AUDITOR = 'AUDITOR', 'Auditor'

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ANALYST)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
