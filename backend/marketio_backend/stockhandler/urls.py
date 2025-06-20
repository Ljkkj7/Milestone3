from django.urls import path, include
from .views import StockListAPIView, StockUpdateAPIView


urlpatterns = [
    path('', StockListAPIView.as_view(), name='stock-list'),
    path('update/', StockUpdateAPIView.as_view(), name='stock-update'),
]