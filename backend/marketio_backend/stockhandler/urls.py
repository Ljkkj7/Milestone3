from django.urls import path, include
from .views import StockListAPIView


urlpatterns = [
    path('', StockListAPIView.as_view()),
    path('update/', StockListAPIView.as_view(), name='stock-update'),
]