from decimal import Decimal
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
    
class PositiveStockMarketEventAPIView(APIView):
    def post(self, request):
        stockAffected = request.data.get("symbol")
        stock = Stock.objects.filter(symbol=stockAffected).first()
        stock.simulate_positive_market_event()
        serializer = StockSerializer(stock)
        return Response(serializer.data)
    
class NegativeStockMarketEventAPIView(APIView):
    def post(self, request):
        stockAffected = request.data.get("symbol")
        stock = Stock.objects.filter(symbol=stockAffected).first()
        stock.simulate_negative_market_event()
        serializer = StockSerializer(stock)
        return Response(serializer.data)
    
class StockMarketEventEndAPIView(APIView):
    def post(self, request):
        stockAffected = request.data.get("symbol")
        stock = Stock.objects.filter(symbol=stockAffected).first()
        stock.market_event_end()
        serializer = StockSerializer(stock)
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

        experience_gain = int(totalCost * (float(2/user_profile.level)))  # Experience gain from buying is halved every level
        user_profile.experience += experience_gain

        if user_profile.experience > ((user_profile.level**2) * 1000):
            while user_profile.experience > 0:
                if user_profile.experience - ((user_profile.level**2) * 1000) < 0:
                    break
                else:
                    user_profile.level += 1
                    user_profile.experience -= (((user_profile.level-1)**2) * 1000)

        user_profile.balance -= totalCost
        user_profile.save()
        
        Transaction.objects.create(
            user_profile=user_profile,
            stock=stock,
            quantity=quantity,
            transaction_type='BUY',
            price=stock.price
        )

        stockOwned = (
            sum(t.quantity for t in Transaction.objects.filter(user_profile=user_profile, stock=stock, transaction_type='BUY'))
            - sum(t.quantity for t in Transaction.objects.filter(user_profile=user_profile, stock=stock, transaction_type='SELL'))
        )

        return Response({'quantity': stockOwned,
                         'price': stock.price,
                         'balance': user_profile.balance
                         })
        



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

        experience_gain = int(totalPrice * Decimal('0.1'))  # Example: 10% of total price as experience
        if experience_gain < 0:
            experience_gain = 0
        user_profile.experience += experience_gain

        if user_profile.experience > ((user_profile.level**2) * 1000):
            while user_profile.experience > 0:
                if user_profile.experience - ((user_profile.level**2) * 1000) < 0:
                    break
                else:
                    user_profile.level += 1
                    user_profile.experience -= (((user_profile.level-1)**2) * 1000)

        user_profile.balance += totalPrice
        user_profile.save()

        Transaction.objects.create(
            user_profile=user_profile,
            stock=stock,
            quantity=quantity,
            transaction_type='SELL',
            price=stock.price
        )

        stockOwned = stockOwned - quantity

        return Response({
            'quantity': stockOwned,
            'price': stock.price,
            'balance': user_profile.balance,
        })