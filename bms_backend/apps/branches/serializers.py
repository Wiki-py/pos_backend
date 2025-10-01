from rest_framework import serializers
from .models import Branch

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'

class BranchStatsSerializer(serializers.Serializer):
    total_employees = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    monthly_growth = serializers.DecimalField(max_digits=5, decimal_places=2)