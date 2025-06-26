from django.shortcuts import render
from stockhandler.models import Transaction, Stock
from custom_auth.models import UserProfile
from custom_auth.serializers import UserProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.


class BalanceLoadView(APIView):
    """
    A view to load a users balance value
    """

    permission_classes = [IsAuthenticated]

    def get(self, req):
        balance = UserProfile.objects.get(user=req.user)
        serializer = UserProfileSerializer(balance)
        return Response(serializer.data)


class PortfolioLoadView(APIView):
    """
    A view to load a users portfolio value
    """
    permission_classes = [IsAuthenticated]

    def get(self, req):
        #user_profile = UserProfile.objects.get(user=req.user)
        #transactions = Transaction.objects.filter(user_profile=user_profile)

        #if not transactions.exists():
        return Response({'total_portfolio_value': 0})