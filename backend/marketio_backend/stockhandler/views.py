from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Stock
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