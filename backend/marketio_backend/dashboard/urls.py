from django.urls import include, path
from .views import BalanceLoadView

urlpatterns = [
    path('', BalanceLoadView.as_view(), name='balance_get')
]