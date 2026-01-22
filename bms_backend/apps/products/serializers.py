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
    stock_status = serializers.SerializerMethodField()
    is_low_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'sku', 'cost_price', 'selling_price',
            'quantity', 'category', 'branch', 'image', 'barcode', 
            'low_stock_threshold', 'is_active', 'created_at', 'updated_at',
            'category_name', 'branch_name', 'profit', 'stock_status', 'is_low_stock'
        ]
        read_only_fields = ('created_at', 'updated_at')

    def get_stock_status(self, obj):
        """
        Calculate stock status based on current stock levels
        """
        current_stock = obj.quantity
        
        if current_stock == 0:
            return 'out_of_stock'
        elif current_stock <= obj.low_stock_threshold:
            return 'low_stock'
        else:
            return 'in_stock'
    
    def get_is_low_stock(self, obj):
        """
        Boolean field to quickly check if product is low on stock
        """
        return obj.quantity <= obj.low_stock_threshold

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'sku', 'cost_price', 'selling_price', 
            'quantity', 'category', 'branch', 'image', 'barcode', 
            'low_stock_threshold', 'is_active'
        ]
    
    def validate_sku(self, value):
        """
        Ensure SKU is unique across all products
        """
        if Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError("Product with this SKU already exists.")
        return value
    
    def validate_quantity(self, value):
        """
        Ensure quantity is not negative
        """
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value

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