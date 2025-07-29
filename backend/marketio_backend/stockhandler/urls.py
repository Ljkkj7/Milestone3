from django.urls import path, include
from .views import StockListAPIView, StockUpdateAPIView, BuyStockView, SellStockView, PositiveStockMarketEventAPIView, NegativeStockMarketEventAPIView, StockMarketEventEndAPIView


urlpatterns = [
    path('', StockListAPIView.as_view(), name='stock-list'),
    path('update/', StockUpdateAPIView.as_view(), name='stock-update'),
    path('buy/', BuyStockView.as_view(), name='stock-buy'),
    path('sell/', SellStockView.as_view(), name='stock-sell'),
    path('update/positive/', PositiveStockMarketEventAPIView.as_view(), name="stock-positive-event"),
    path('update/negative/', NegativeStockMarketEventAPIView.as_view(), name="stock-negative-event"),
    path('update/eventend/', StockMarketEventEndAPIView.as_view(), name="stock-event-end")
]