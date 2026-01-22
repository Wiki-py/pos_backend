from rest_framework import viewsets, permissions
from .models import Product, Category
from .serializers import (
    ProductSerializer, ProductCreateSerializer, 
    CategorySerializer, LowStockAlertSerializer,
    StockAdjustmentSerializer
)
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F, Q, Sum
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, filters
from .filters import ProductFilter

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'selling_price', 'quantity', 'created_at']
    stock_status = ['in_stock', 'low_stock', 'out_of_stock']

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        return ProductSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Product.objects.filter(is_active=True)
        if user.role == 'admin':
            return queryset
        elif user.role == 'manager':
            return queryset.filter(branch=user.branch)
        return queryset.filter(branch=user.branch)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        low_stock_products = self.get_queryset().filter(
            quantity__gt=0, 
            quantity__lte=F('low_stock_threshold')
        ).values(
            'id', 'name', 'quantity', 'low_stock_threshold', 'branch__name'
        ).annotate(
            product_id=F('id'),
            product_name=F('name'),
            current_stock=F('quantity'),
            threshold=F('low_stock_threshold'),
            branch_name=F('branch__name')
        )
        serializer = LowStockAlertSerializer(low_stock_products, many=True)
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
    
    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """Adjust stock with transaction type"""
        product = self.get_object()
        serializer = StockAdjustmentSerializer(data=request.data)
        
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            transaction_type = serializer.validated_data['transaction_type']
            
            if transaction_type == 'in':
                product.quantity += quantity
            elif transaction_type == 'out':
                if product.quantity >= quantity:
                    product.quantity -= quantity
                else:
                    return Response(
                        {"error": "Insufficient stock"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            product.save()
            return Response(ProductSerializer(product).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced product search"""
        query = request.GET.get('q', '')
        category = request.GET.get('category')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        
        queryset = self.get_queryset()
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | 
                Q(sku__icontains=query) | 
                Q(description__icontains=query)
            )
        
        if category:
            queryset = queryset.filter(category_id=category)
        
        if min_price:
            queryset = queryset.filter(selling_price__gte=min_price)
        
        if max_price:
            queryset = queryset.filter(selling_price__lte=max_price)
        
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get product dashboard statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_products': queryset.count(),
            'low_stock_count': queryset.filter(
                quantity__gt=0, 
                quantity__lte=F('low_stock_threshold')
            ).count(),
            'out_of_stock_count': queryset.filter(quantity=0).count(),
            'total_value': queryset.aggregate(
                total=Sum(F('quantity') * F('selling_price'))
            )['total'] or 0,
            'categories_count': Category.objects.count()
        }
        
        return Response(stats)