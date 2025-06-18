from django.urls import path, include
from .views import StockListAPIView


urlpatterns = [
    path('', StockListAPIView.as_view()),
]