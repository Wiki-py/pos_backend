# apps/branches/serializers.py
from rest_framework import serializers
from django.db.models import Sum
from apps.sales.models import Sale
from .models import Branch

class BranchSerializer(serializers.ModelSerializer):
    revenue = serializers.SerializerMethodField()
    growth = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    
    class Meta:
        model = Branch
        fields = '__all__'
    
    def get_type(self, obj):
        # Use existing type or determine from name
        if obj.type:
            return obj.type
        
        name_lower = obj.name.lower()
        if any(word in name_lower for word in ['electronic', 'tech', 'computer']):
            return 'Electronics'
        elif any(word in name_lower for word in ['clothing', 'fashion', 'apparel']):
            return 'Clothing'
        elif any(word in name_lower for word in ['cafe', 'restaurant', 'food', 'coffee']):
            return 'Food'
        return 'General'
    
    def get_revenue(self, obj):
        total_sales = Sale.objects.filter(branch=obj).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        return float(total_sales)
    
    def get_growth(self, obj):
        return 8.5  # Static for now

class BranchStatsSerializer(serializers.Serializer):
    total_employees = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    monthly_growth = serializers.DecimalField(max_digits=5, decimal_places=2)