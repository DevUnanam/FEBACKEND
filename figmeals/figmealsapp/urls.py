from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SignupView, LoginView, MealViewSet, OrderViewSet, AdminOrderUpdateView
from rest_framework.authtoken.views import obtain_auth_token

# Routers for meals and orders
router = DefaultRouter()
router.register(r'meals', MealViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('orders/<int:pk>/', AdminOrderUpdateView.as_view(), name='order-update'),
    path('api/token-auth/', obtain_auth_token, name='api_token_auth'),
]

# Add router-generated URLs to urlpatterns
urlpatterns += router.urls
