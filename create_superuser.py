#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create superuser
user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@example.com',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
    }
)

if created:
    user.set_password('admin123')
    user.save()
    print("Superuser created: admin / admin123")
else:
    user.is_superuser = True
    user.set_password('admin123')
    user.save()
    print("Superuser updated: admin / admin123")
