from rest_framework import serializers
from .models import Product, Category
from apps.inventory.models import InventoryTransaction

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    profit = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    stock_status = serializers.SerializerMethodField()  # Changed to SerializerMethodField

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_stock_status(self, obj):
        """
        Calculate stock status based on current stock levels
        """
        # If you have a quantity field
        if hasattr(obj, 'quantity'):
            current_stock = obj.quantity
        # If you have a current_stock field  
        elif hasattr(obj, 'current_stock'):
            current_stock = obj.current_stock
        else:
            return 'unknown'
        
        # If you have low_stock_threshold field
        if hasattr(obj, 'low_stock_threshold') and obj.low_stock_threshold:
            if current_stock <= obj.low_stock_threshold:
                return 'low'
            elif current_stock == 0:
                return 'out_of_stock'
            else:
                return 'in_stock'
        else:
            # Default logic if no threshold
            if current_stock <= 0:
                return 'out_of_stock'
            elif current_stock <= 10:  # Default low stock threshold
                return 'low'
            else:
                return 'in_stock'

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('name', 'description', 'sku', 'cost_price', 'selling_price', 
                 'quantity', 'category', 'branch', 'image', 'barcode', 'low_stock_threshold')

class LowStockAlertSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    current_stock = serializers.IntegerField()
    threshold = serializers.IntegerField()
    branch_name = serializers.CharField()

class StockAdjustmentSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField()
    transaction_type = serializers.ChoiceField(choices=InventoryTransaction.TRANSACTION_TYPES)
    reason = serializers.CharField(allow_blank=True, required=False)