from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Sale, SaleItem
from .serializers import (
    SaleSerializer, SaleCreateSerializer, 
    DailySalesReportSerializer
)

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return SaleCreateSerializer
        return SaleSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Sale.objects.all()
        elif user.role == 'manager':
            return Sale.objects.filter(branch=user.branch)
        return Sale.objects.filter(processed_by=user)

    def perform_create(self, serializer):
        serializer.save(processed_by=self.request.user)

    @action(detail=False, methods=['get'])
    def today_sales(self, request):
        today = timezone.now().date()
        today_sales = self.get_queryset().filter(sale_date__date=today)
        
        total_sales = today_sales.aggregate(
            total_amount=Sum('total_amount'),
            total_transactions=Count('id')
        )
        
        return Response({
            'date': today,
            'total_sales': total_sales['total_amount'] or 0,
            'total_transactions': total_sales['total_transactions'] or 0,
            'average_transaction': (total_sales['total_amount'] or 0) / (total_sales['total_transactions'] or 1)
        })

    @action(detail=False, methods=['get'])
    def sales_report(self, request):
        # Get date range from query params
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                sales = self.get_queryset().filter(
                    sale_date__date__range=[start_date, end_date]
                )
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Default to last 30 days
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
            sales = self.get_queryset().filter(
                sale_date__date__range=[start_date, end_date]
            )
        
        report_data = sales.aggregate(
            total_sales=Sum('total_amount'),
            total_transactions=Count('id'),
            average_tax=Sum('tax_amount'),
            average_discount=Sum('discount_amount')
        )
        
        # Sales by payment method
        payment_methods = sales.values('payment_method').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        )
        
        # Daily breakdown
        daily_sales = sales.values('sale_date__date').annotate(
            daily_total=Sum('total_amount'),
            daily_count=Count('id')
        ).order_by('sale_date__date')
        
        return Response({
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': report_data,
            'payment_methods': payment_methods,
            'daily_breakdown': daily_sales
        })

    @action(detail=True, methods=['get'])
    def receipt(self, request, pk=None):
        sale = self.get_object()
        serializer = SaleSerializer(sale)
        return Response(serializer.data)