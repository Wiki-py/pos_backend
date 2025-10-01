import openpyxl
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Report
from .serializers import ReportSerializer, ReportGenerateSerializer
from apps.sales.models import Sale
from apps.products.models import Product
from apps.inventory.models import InventoryTransaction

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Report.objects.all()
        elif user.role == 'manager':
            return Report.objects.filter(branch=user.branch)
        return Report.objects.filter(generated_by=user)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        serializer = ReportGenerateSerializer(data=request.data)
        if serializer.is_valid():
            report_type = serializer.validated_data['report_type']
            branch = serializer.validated_data.get('branch')
            start_date = serializer.validated_data.get('start_date')
            end_date = serializer.validated_data.get('end_date')
            period = serializer.validated_data.get('period')
            export_format = serializer.validated_data.get('export_format', 'json')

            # Generate report data based on type
            if report_type == 'sales':
                report_data = self._generate_sales_report(branch, start_date, end_date)
            elif report_type == 'inventory':
                report_data = self._generate_inventory_report(branch)
            elif report_type == 'customer':
                report_data = self._generate_customer_report(branch, start_date, end_date)
            else:
                report_data = self._generate_financial_report(branch, start_date, end_date)

            # Create report record
            report = Report.objects.create(
                name=f"{report_type.title()} Report",
                report_type=report_type,
                branch=branch,
                period=period or f"{start_date} to {end_date}" if start_date and end_date else "Custom",
                generated_by=request.user,
                data=report_data
            )

            if export_format in ['pdf', 'excel']:
                file_content = self._export_report(report, export_format)
                report.is_exported = True
                report.file_path.save(f'report_{report.id}.{export_format}', file_content)
                report.save()

            return Response(ReportSerializer(report).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _generate_sales_report(self, branch, start_date, end_date):
        # Filter sales by branch and date range
        sales_query = Sale.objects.all()
        if branch:
            sales_query = sales_query.filter(branch=branch)
        if start_date and end_date:
            sales_query = sales_query.filter(sale_date__date__range=[start_date, end_date])

        sales_data = sales_query.aggregate(
            total_revenue=Sum('total_amount'),
            total_transactions=Count('id'),
            average_sale=Avg('total_amount'),
            total_tax=Sum('tax_amount'),
            total_discount=Sum('discount_amount')
        )

        # Sales by payment method
        payment_methods = sales_query.values('payment_method').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        )

        # Daily breakdown
        daily_sales = sales_query.values('sale_date__date').annotate(
            daily_total=Sum('total_amount'),
            daily_count=Count('id')
        ).order_by('sale_date__date')

        return {
            'summary': sales_data,
            'payment_methods': list(payment_methods),
            'daily_breakdown': list(daily_sales),
            'total_profit': (sales_data['total_revenue'] or 0) - (sales_data['total_tax'] or 0)
        }

    def _generate_inventory_report(self, branch):
        products_query = Product.objects.filter(is_active=True)
        if branch:
            products_query = products_query.filter(branch=branch)

        inventory_data = products_query.aggregate(
            total_products=Count('id'),
            total_value=Sum('selling_price'),
            low_stock_count=Count('id', filter=models.Q(quantity__gt=0, quantity__lte=models.F('low_stock_threshold'))),
            out_of_stock_count=Count('id', filter=models.Q(quantity=0))
        )

        # Category breakdown
        categories = products_query.values('category__name').annotate(
            count=Count('id'),
            total_value=Sum('selling_price')
        )

        return {
            'summary': inventory_data,
            'categories': list(categories),
            'low_stock_alerts': list(products_query.filter(
                quantity__gt=0, 
                quantity__lte=models.F('low_stock_threshold')
            ).values('name', 'quantity', 'low_stock_threshold'))
        }

    def _generate_customer_report(self, branch, start_date, end_date):
        sales_query = Sale.objects.all()
        if branch:
            sales_query = sales_query.filter(branch=branch)
        if start_date and end_date:
            sales_query = sales_query.filter(sale_date__date__range=[start_date, end_date])

        customer_data = sales_query.values('customer_name', 'customer_email').annotate(
            total_spent=Sum('total_amount'),
            visit_count=Count('id'),
            average_spent=Avg('total_amount')
        ).order_by('-total_spent')

        return {
            'top_customers': list(customer_data[:10]),
            'total_customers': customer_data.count(),
            'customer_satisfaction': 85  # This would come from feedback system
        }

    def _generate_financial_report(self, branch, start_date, end_date):
        sales_data = self._generate_sales_report(branch, start_date, end_date)
        inventory_data = self._generate_inventory_report(branch)

        # Calculate expenses (this would come from an expenses model)
        estimated_expenses = (sales_data['summary']['total_revenue'] or 0) * 0.3  # 30% estimate

        return {
            'revenue': sales_data['summary']['total_revenue'] or 0,
            'expenses': estimated_expenses,
            'profit': (sales_data['summary']['total_revenue'] or 0) - estimated_expenses,
            'inventory_value': inventory_data['summary']['total_value'] or 0,
            'gross_margin': ((sales_data['summary']['total_revenue'] or 0) - estimated_expenses) / (sales_data['summary']['total_revenue'] or 1) * 100
        }

    def _export_report(self, report, format_type):
        if format_type == 'excel':
            return self._export_to_excel(report)
        else:  # pdf
            return self._export_to_pdf(report)

    def _export_to_excel(self, report):
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = report.report_type.title()

        # Add headers based on report type
        if report.report_type == 'sales':
            worksheet.append(['Date', 'Total Revenue', 'Transactions', 'Average Sale'])
            for daily in report.data.get('daily_breakdown', []):
                worksheet.append([
                    daily['sale_date__date'],
                    daily['daily_total'],
                    daily['daily_count'],
                    daily['daily_total'] / daily['daily_count'] if daily['daily_count'] > 0 else 0
                ])

        buffer = BytesIO()
        workbook.save(buffer)
        return buffer

    def _export_to_pdf(self, report):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        p.drawString(100, 750, f"Report: {report.name}")
        p.drawString(100, 730, f"Type: {report.report_type}")
        p.drawString(100, 710, f"Period: {report.period}")
        p.drawString(100, 690, f"Generated: {report.generated_at}")
        
        # Add report data
        y_position = 650
        for key, value in report.data.items():
            if y_position < 100:
                p.showPage()
                y_position = 750
            p.drawString(100, y_position, f"{key}: {value}")
            y_position -= 20

        p.save()
        return buffer

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        report = self.get_object()
        if report.file_path:
            response = HttpResponse(report.file_path.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{report.file_path.name}"'
            return response
        return Response({"error": "No exported file available"}, status=status.HTTP_404_NOT_FOUND)