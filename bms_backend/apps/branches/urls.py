from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BranchViewSet

router = DefaultRouter()
router.register(r'', BranchViewSet)

urlpatterns = [
    path('', include(router.urls)),
]