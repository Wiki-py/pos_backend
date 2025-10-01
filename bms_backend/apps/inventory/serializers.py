from rest_framework import serializers
from .models import InventoryTransaction
from .models import Product

class InventoryTransactionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)

    class Meta:
        model = InventoryTransaction
        fields = '__all__'
        read_only_fields = ('previous_stock', 'new_stock', 'transaction_date')

class StockAdjustmentSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField()
    reason = serializers.CharField(required=False, allow_blank=True)
    transaction_type = serializers.ChoiceField(choices=InventoryTransaction.TRANSACTION_TYPES)