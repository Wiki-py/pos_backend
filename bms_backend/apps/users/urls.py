from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserViewSet

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-list'),
    path('users/profile/', UserViewSet.as_view({'get': 'profile'}), name='user-profile')

    
]