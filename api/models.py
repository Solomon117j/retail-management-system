from django.db import models
from django.utils import timezone

class APIKey(models.Model):
    name = models.CharField(max_length=100, verbose_name="API Key Name")
    key = models.CharField(max_length=255, unique=True, verbose_name="API Key")
    is_active = models.BooleanField(default=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(blank=True, null=True)
    rate_limit = models.PositiveIntegerField(
        default=1000,
        verbose_name="Rate Limit (requests per hour)"
    )

    def __str__(self):
        return self.name

class APIRequestLog(models.Model):
    api_key = models.ForeignKey(
        APIKey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status_code = models.PositiveIntegerField()
    response_time = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        verbose_name="Response Time (seconds)"
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"

class Webhook(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()
    event_type = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    secret = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
