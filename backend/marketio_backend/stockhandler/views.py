from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Stock, Transaction
from custom_auth.models import UserProfile
from .serializers import StockSerializer

# Create your views here.

class StockListAPIView(APIView):
    def get(self, request):
        stocks = Stock.objects.all()
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)
    
class StockUpdateAPIView(APIView):
    def post(self, request):
        stocks = Stock.objects.all()
        for stock in stocks:
            stock.simulate_price_change()
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)
    
class BuyStockView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
        symbol = request.data.get("symbol")
        quantity = int(request.data.get("quantity"))

        if not symbol or not quantity:
            return Response({'error': 'Symbol and quantity are requred.'})
        
        try:
            if quantity <= 0:
                return Response({'error': 'Quantity must be positive'})
        except ValueError:
            return Response({'error': 'Quantity must be an integer'})
        
        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            return Response({'error': 'Stock not found'})
        
        totalCost = stock.price * quantity

        if user_profile.balance < totalCost:
            return Response({'error': 'Insufficient balance'})
        
        user_profile.balance -= totalCost
        user_profile.save()

        Transaction.objects.create(
            user_profile=user_profile,
            stock=stock,
            quantity=quantity,
            transaction_type='BUY',
            price=stock.price
        )

        return Response({'message': f'Successfully bought {quantity} shares of {symbol}'})
        



class SellStockView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
        symbol = request.data.get("symbol")
        quantity = int(request.data.get("quantity"))

        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            return Response({'error': 'Stock not found'})
        
        
        stockOwned = (
            sum(t.quantity for t in Transaction.objects.filter(user_profile=user_profile, stock=stock, transaction_type='BUY'))
            - sum(t.quantity for t in Transaction.objects.filter(user_profile=user_profile, stock=stock, transaction_type='SELL'))
        )

        if not symbol or not quantity:
            return Response({'error': 'Symbol and quantity are requred.'})
        
        try:
            if quantity <= 0:
                return Response({'error': 'Quantity must be positive'})
            elif quantity > stockOwned:
                return Response({'error': 'Not enough stock to sell'})
        except ValueError:
            return Response({'error': 'Quantity must be an integer'})
        
        
        totalPrice = stock.price * quantity

        user_profile.balance += totalPrice
        user_profile.save()

        Transaction.objects.create(
            user_profile=user_profile,
            stock=stock,
            quantity=quantity,
            transaction_type='SELL',
            price=stock.price
        )

        return Response({
            'quantity': quantity,
            'price': stock.price
        })