import uuid
from django.contrib.auth.models import Group, Permission
from django.db import models
from django.contrib.auth.models import AbstractUser

from retail_management_system import settings

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_customer = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group, related_name="account_users", blank=True, verbose_name='groups', help_text='The groups this user belongs to...'
    )
    user_permissions = models.ManyToManyField(
        Permission, related_name="account_users", blank=True, verbose_name='user permissions', help_text='Specific permissions for the user...'
    )

class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # Customer-specific fields
    loyalty_points = models.IntegerField(default=0)

class Employee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        null=True,
        blank=True
    )
    # Employee-specific fields
    department = models.CharField(max_length=100)
