from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum
from .models import Branch
from .serializers import BranchSerializer, BranchStatsSerializer
from apps.users.models import User
from apps.products.models import Product
from apps.sales.models import Sale

class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.filter(is_active=True)
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        branch = self.get_object()
        
        # Calculate stats
        total_employees = User.objects.filter(branch=branch, is_active=True).count()
        total_products = Product.objects.filter(branch=branch).count()
        
        sales_data = Sale.objects.filter(branch=branch).aggregate(
            total_sales=Sum('total_amount')
        )
        total_sales = sales_data['total_sales'] or 0
        
        # Mock monthly growth calculation
        monthly_growth = 8.5  # This would be calculated from actual data
        
        stats_data = {
            'total_employees': total_employees,
            'total_products': total_products,
            'total_sales': total_sales,
            'monthly_growth': monthly_growth
        }
        
        serializer = BranchStatsSerializer(stats_data)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        branch = self.get_object()
        employees = User.objects.filter(branch=branch, is_active=True)
        from apps.users.serializers import UserSerializer
        serializer = UserSerializer(employees, many=True)
        return Response(serializer.data)
    
