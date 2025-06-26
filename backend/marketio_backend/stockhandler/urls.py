from django.urls import path, include
from .views import StockListAPIView, StockUpdateAPIView, BuyStockView, SellStockView


urlpatterns = [
    path('', StockListAPIView.as_view(), name='stock-list'),
    path('update/', StockUpdateAPIView.as_view(), name='stock-update'),
    path('buy/', BuyStockView.as_view(), name='stock-buy'),
    path('sell/', SellStockView.as_view(), name='stock-sell'),
]