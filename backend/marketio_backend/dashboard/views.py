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
        user_profile = UserProfile.objects.get(user=req.user)
        transactions = Transaction.objects.filter(user_profile=user_profile)

        if not transactions.exists():
            return Response({'total_portfolio_value': 0})
        
        # Build portfolio: {symbol: net_Quantity}
        portfolio = {}

        for tx in transactions:
            symbol = tx.stock.symbol
            portfolio.setdefault(symbol, 0)
            if tx.transaction_type == 'BUY':
                portfolio[symbol] += tx.quantity
            elif tx.transaction_type == 'SELL':
                portfolio[symbol] -= tx.quantity
        
        totalValue = 0
        details = []

        for symbol, quantity in portfolio.items():
            if quantity <= 0:
                continue
            try:
                stock = Stock.objects.get(symbol=symbol)
                stockValue = stock.price * quantity
                totalValue += stockValue
                details.append({
                    'symbol': symbol,
                    'quantity': quantity,
                    'current_price': stock.price,
                    'value': stockValue
                })
            except Stock.DoesNotExist:
                continue
        
        return Response({
            'total_portfolio_value': totalValue,
            'details': details
        })

            