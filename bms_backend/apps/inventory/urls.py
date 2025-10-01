from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryTransactionViewSet

router = DefaultRouter()
router.register(r'transactions', InventoryTransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]