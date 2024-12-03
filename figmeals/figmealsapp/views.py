from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Meal, Order
from .serializers import UserSerializer, MealSerializer, OrderSerializer

# Authentication Views
@method_decorator(csrf_exempt, name='dispatch')
class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User created successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.authtoken.models import Token

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            # Generate or retrieve the token for the user
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'message': 'Login successful!'}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# Meal Management Views
class MealViewSet(viewsets.ModelViewSet):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer

    # Only authenticated users can view meals, but only admins can create/update/delete meals.
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            # Only allow admins to perform create, update, or delete actions.
            return [IsAdminUser()]
        # Allow authenticated users to view meals.
        return [IsAuthenticated()]

# Order Management Views
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access orders

    def get_queryset(self):
        """
        This method returns orders specific to the logged-in user.
        Admins will have access to all orders, but regular users will only see their own.
        """
        user = self.request.user
        if user.is_authenticated:
            # For regular users (customers), show only their own orders.
            if user.is_staff:  # If the user is an admin (staff), they can view all orders.
                return Order.objects.all()
            return Order.objects.filter(user=user)
        return Order.objects.none()

    def retrieve(self, request, *args, **kwargs):
        """
        Custom retrieve method to ensure that users can only view their own orders.
        Admins can view any order.
        """
        order = self.get_object()
        if order.user != request.user and not request.user.is_staff:  # Only allow admins to view others' orders
            return Response({'error': 'You do not have permission to view this order.'}, status=status.HTTP_403_FORBIDDEN)
        return super().retrieve(request, *args, **kwargs)
class AdminOrderUpdateView(APIView):
    def put(self, request, pk):
        order = get_object_or_404(Order, id=pk)
        order.status = request.data.get('status')
        order.save()
        return Response({'message': 'Order status updated!'}, status=status.HTTP_200_OK)
