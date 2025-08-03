from django.contrib import admin

from .models import Customer, LoyaltyTransaction, Sale, SaleItem, Return
# Register your models here.
admin.site.register(Customer)
admin.site.register(LoyaltyTransaction)
admin.site.register(Sale)   
admin.site.register(SaleItem)
admin.site.register(Return) 