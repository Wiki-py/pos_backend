from django_filters import rest_framework as filters
from .models import Product
from django.db.models import F

class ProductFilter(filters.FilterSet):
    stock_status = filters.CharFilter(method='filter_stock_status')

    class Meta:
        model = Product
        fields = ['category', 'branch', 'stock_status']

    def filter_stock_status(self, queryset, name, value):
        if value == 'in_stock':
            return queryset.filter(quantity__gt=F('low_stock_threshold'))
        elif value == 'low_stock':
            return queryset.filter(quantity__gt=0, quantity__lte=F('low_stock_threshold'))
        elif value == 'out_of_stock':
            return queryset.filter(quantity=0)
        return queryset
    


class ProductFilter(filters.FilterSet):
    stock_status = filters.CharFilter(method='filter_stock_status')

    class Meta:
        model = Product
        fields = ['category', 'branch', 'stock_status']

    def filter_stock_status(self, queryset, name, value):
        if value == 'in_stock':
            return queryset.filter(quantity__gt=F('low_stock_threshold'))
        elif value == 'low_stock':
            return queryset.filter(quantity__gt=0, quantity__lte=F('low_stock_threshold'))
        elif value == 'out_of_stock':
            return queryset.filter(quantity=0)
        return queryset