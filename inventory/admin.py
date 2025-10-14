from django.contrib import admin
from .models import Brand, Category, Product, InventoryRecord, StockMovement

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'brand', 'unit_price', 'reorder_level', 'is_active', 'created_at')
    list_filter = ('category', 'brand', 'is_active')
    search_fields = ('name', 'sku')

@admin.register(InventoryRecord)
class InventoryRecordAdmin(admin.ModelAdmin):
    list_display = ('product', 'store', 'quantity', 'location', 'created_at', 'updated_at')
    list_filter = ('store', 'location')
    search_fields = ('product__name',)

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'store', 'quantity', 'movement_type', 'created_by', 'created_at')
    list_filter = ('movement_type', 'store')
    search_fields = ('product__name', 'reason')
