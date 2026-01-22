# apps/branches/serializers.py
from rest_framework import serializers
from django.db.models import Sum, Count
from apps.sales.models import Sale
from apps.products.models import Product
from .models import Branch
from django.db import models

class BranchSerializer(serializers.ModelSerializer):
    total_products = serializers.SerializerMethodField()
    total_sales = serializers.SerializerMethodField()
    total_revenue = serializers.SerializerMethodField()
    active_products = serializers.SerializerMethodField()
    low_stock_products = serializers.SerializerMethodField()
    
    class Meta:
        model = Branch
        fields = [
            'id', 'name', 'type', 'location', 'address', 'phone', 'email',
            'manager', 'opening_date', 'capacity', 'description', 'color_theme',
            'is_active', 'created_at', 'updated_at', 'total_products', 
            'total_sales', 'total_revenue', 'active_products', 'low_stock_products'
        ]
        read_only_fields = ('created_at', 'updated_at')
    
    def get_total_products(self, obj):
        """Get total number of products in this branch"""
        return Product.objects.filter(branch=obj).count()
    
    def get_total_sales(self, obj):
        """Get total number of sales for this branch"""
        return Sale.objects.filter(branch=obj).count()
    
    def get_total_revenue(self, obj):
        """Get total revenue for this branch"""
        total_sales = Sale.objects.filter(branch=obj).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        return float(total_sales)
    
    def get_active_products(self, obj):
        """Get number of active products in this branch"""
        return Product.objects.filter(branch=obj, is_active=True).count()
    
    def get_low_stock_products(self, obj):
        """Get number of products with low stock in this branch"""
        return Product.objects.filter(
            branch=obj, 
            is_active=True,
            quantity__lte=models.F('low_stock_threshold')
        ).count()

class BranchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = [
            'name', 'type', 'location', 'address', 'phone', 'email',
            'manager', 'opening_date', 'capacity', 'description', 
            'color_theme', 'is_active'
        ]
    
    def validate_phone(self, value):
        """Validate phone number format"""
        if value and not value.replace('-', '').replace(' ', '').isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        return value
    
    def validate_capacity(self, value):
        """Ensure capacity is not negative"""
        if value < 0:
            raise serializers.ValidationError("Capacity cannot be negative.")
        return value

class BranchStatsSerializer(serializers.Serializer):
    total_employees = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    monthly_growth = serializers.DecimalField(max_digits=5, decimal_places=2)

class BranchPerformanceSerializer(serializers.ModelSerializer):
    """Serializer for branch performance analytics"""
    revenue = serializers.SerializerMethodField()
    sales_count = serializers.SerializerMethodField()
    average_sale_value = serializers.SerializerMethodField()
    top_products = serializers.SerializerMethodField()
    
    class Meta:
        model = Branch
        fields = ['id', 'name', 'location', 'revenue', 'sales_count', 
                 'average_sale_value', 'top_products']
    
    def get_revenue(self, obj):
        total_sales = Sale.objects.filter(branch=obj).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        return float(total_sales)
    
    def get_sales_count(self, obj):
        return Sale.objects.filter(branch=obj).count()
    
    def get_average_sale_value(self, obj):
        sales = Sale.objects.filter(branch=obj)
        if not sales.exists():
            return 0
        total = sales.aggregate(total=Sum('total_amount'))['total'] or 0
        return float(total / sales.count())
    
    def get_top_products(self, obj):
        """Get top 5 selling products for this branch"""
        # This would need to be implemented based on your sales data structure
        return []  # Placeholder