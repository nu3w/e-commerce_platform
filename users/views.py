from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework.authtoken.models import Token

from .serializers import RegisterSerializers
from .permissions import IsAdmin, IsSupplier, IsCustomer, IsDeliveryPersonnel

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema( 
        request=RegisterSerializers, 
        responses={201: dict}
    )
    
    def post(self, request):
        serializer = RegisterSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "User registered successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                }
            },
            status=status.HTTP_201_CREATED
        )

class LoginView(APIView):
    permission_classes = [AllowAny]
    
            
    @extend_schema(
        request=inline_serializer(
            name="LoginRequest",
            fields={
                "username": serializers.CharField(),
                "password": serializers.CharField(),
            },
        ),
        responses={200:dict, 401: dict}
    )
    
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        user = authenticate(
            username = username,
            password = password
        )
        
        if user is None:
            return Response(
                {
                    "detail": "Invalid username or password."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        token, created = Token.objects.get_or_create(user=user)
        
        return Response(
            {
                "message": "Login successful",
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                }
            },
            status=status.HTTP_200_OK
        )
        
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(responses=dict)
    
    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "role": request.user.role,
        })
        
class CustomerTestView(APIView):
    permission_classes = [IsCustomer]
    
    @extend_schema(responses=dict)
    
    def get(self, request):
        return Response({
            "message": "You are allowed to access the customer area.",
            "user": request.user.username,
            "role": request.user.role,
        })
        
class SupplierTestView(APIView):
    permission_classes = [IsSupplier]
    
    @extend_schema(responses=dict)
    
    def get(self, request):
        return Response({
            "message": "You are allowed to access the supplier area.",
            "user": request.user.username,
            "role": request.user.role,
        })
        
class DeliveryPersonnelTestView(APIView):
    permission_classes = [IsDeliveryPersonnel]
    
    @extend_schema(responses=dict)
    
    def get(self, request):
        return Response({
            "message": "You are allowed to access the delivery area.",
            "user": request.user.username,
            "role": request.user.role,
        })
        
class AdminTestView(APIView):
    permission_classes = [IsAdmin]
    
    @extend_schema(responses=dict)
    
    def get(self, request):
        return Response({
            "message": "You are allowed to access admin area.",
            "user": request.user.username,
            "role": request.user.role,
        })