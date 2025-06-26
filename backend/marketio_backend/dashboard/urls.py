from django.urls import include, path
from .views import BalanceLoadView

urlpatterns = [
    path('balance/', BalanceLoadView.as_view(), name='balance_get')
]