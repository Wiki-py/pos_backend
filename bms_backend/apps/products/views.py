from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Product, Category
from .serializers import (
    ProductSerializer, ProductCreateSerializer, 
    CategorySerializer, LowStockAlertSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'branch', 'stock_status']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'selling_price', 'quantity', 'created_at']
    stocl_status = ['in_stock', 'low_stock', 'out_of_stock']

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        return ProductSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Product.objects.filter(is_active=True)
        elif user.role == 'manager':
            return Product.objects.filter(branch=user.branch, is_active=True)
        return Product.objects.filter(branch=user.branch, is_active=True)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        low_stock_products = self.get_queryset().filter(
            quantity__gt=0, 
            quantity__lte=models.F('low_stock_threshold')
        )
        
        alerts = []
        for product in low_stock_products:
            alerts.append({
                'product_id': product.id,
                'product_name': product.name,
                'current_stock': product.quantity,
                'threshold': product.low_stock_threshold,
                'branch_name': product.branch.name
            })
        
        serializer = LowStockAlertSerializer(alerts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        out_of_stock_products = self.get_queryset().filter(quantity=0)
        serializer = ProductSerializer(out_of_stock_products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        product = self.get_object()
        new_quantity = request.data.get('quantity')
        
        if new_quantity is None:
            return Response(
                {"error": "Quantity is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product.quantity = int(new_quantity)
            product.save()
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {"error": "Invalid quantity"}, 
                status=status.HTTP_400_BAD_REQUEST
            )