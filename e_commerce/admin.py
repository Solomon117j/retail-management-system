from django.contrib import admin

from .models import OrderItem, OnlineOrder

# Register your models here.
admin.site.register(OnlineOrder)
admin.site.register(OrderItem)