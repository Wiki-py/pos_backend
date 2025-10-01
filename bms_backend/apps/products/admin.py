from django.contrib import admin
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('created_at',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'branch', 'selling_price', 'quantity', 'stock_status', 'is_active', 'created_at')
    list_filter = ('category', 'branch', 'is_active', 'created_at')
    search_fields = ('name', 'sku', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'sku', 'cost_price', 'selling_price', 
                       'quantity', 'category', 'branch', 'image', 'barcode', 
                       'low_stock_threshold', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
