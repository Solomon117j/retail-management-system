from django.contrib import admin

# Register your models here.

from .models import Product, Category, Brand, StoreInventory, StockMovement
from .forms import ProductForm

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ['name', 'category', 'brand', 'unit_price', 'available_online', 'is_perishable']
    list_filter = ['available_online', 'is_perishable', 'category', 'brand']
    search_fields = ['name', 'description', 'barcode']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'brand')
        }),
        ('Pricing', {
            'fields': ('unit_price', 'cost_price')
        }),
        ('Physical Properties', {
            'fields': ('weight', 'dimensions', 'is_perishable')
        }),
        ('E-commerce', {
            'fields': ('image', 'available_online')
        }),
        ('Identification', {
            'fields': ('barcode',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(StoreInventory)
admin.site.register(StockMovement)
