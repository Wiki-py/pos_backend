from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.branches import views
from django.views import View
from django.http import JsonResponse



class MockDataView(View):
    def get(self, request, *args, **kwargs):
        # Return mock data for missing endpoints
        return JsonResponse({"message": "Mock data - implement proper endpoint"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/users/', include('apps.users.user_urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/inventory/', include('apps.inventory.urls')),
    path('api/sales/', include('apps.sales.urls')),
    path('api/branches/', include('apps.branches.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #path('<int:pk>/stats/', views.BranchStats.as_view(), name='branch-stats'),
    #path('<int:pk>/employees/', views.BranchEmployees.as_view(), name='branch-employees'),
    #path('<int:pk>/sales/', views.BranchSales.as_view(), name='branch-sales'),
    #path('<int:pk>/inventory/', views.BranchInventory.as_view(), name='branch-inventory'),
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)