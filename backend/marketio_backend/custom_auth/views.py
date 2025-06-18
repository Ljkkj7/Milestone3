import requests
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import RegisterSerializer, UserProfileSerializer
from .models import UserProfile
from decimal import Decimal

# Create your views here.

class RegisterView(APIView):
    """
    View to handle user registration.
    """
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        if not username or not email:
            return Response({"error": "Username and email are required."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            profile, created = UserProfile.objects.get_or_create(user=user)
            return Response({
                "message": "User registered successfully.",
                "username": user.username,
                "email": user.email,
                "balance": profile.balance
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)