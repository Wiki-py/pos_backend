from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import InventoryTransaction
from .serializers import InventoryTransactionSerializer, StockAdjustmentSerializer

class InventoryTransactionViewSet(viewsets.ModelViewSet):
    queryset = InventoryTransaction.objects.all()
    serializer_class = InventoryTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return InventoryTransaction.objects.all()
        elif user.role == 'manager':
            return InventoryTransaction.objects.filter(branch=user.branch)
        return InventoryTransaction.objects.filter(performed_by=user)

    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)

    @action(detail=False, methods=['post'])
    def adjust_stock(self, request):
        serializer = StockAdjustmentSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']
            reason = serializer.validated_data.get('reason', '')
            transaction_type = serializer.validated_data['transaction_type']

            # Check if user has permission for this branch
            if request.user.role in ['staff', 'cashier'] and product.branch != request.user.branch:
                return Response(
                    {"error": "You can only adjust stock for your branch"},
                    status=status.HTTP_403_FORBIDDEN
                )

            transaction = InventoryTransaction.objects.create(
                product=product,
                branch=product.branch,
                transaction_type=transaction_type,
                quantity=quantity,
                reason=reason,
                performed_by=request.user
            )

            return Response(InventoryTransactionSerializer(transaction).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        recent_transactions = self.get_queryset().order_by('-transaction_date')[:50]
        serializer = self.get_serializer(recent_transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stock_movements(self, request):
        # Get stock movements for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        movements = self.get_queryset().filter(
            transaction_date__gte=thirty_days_ago
        ).values('product__name', 'transaction_type').annotate(
            total_quantity=Sum('quantity')
        )
        
        return Response(movements)