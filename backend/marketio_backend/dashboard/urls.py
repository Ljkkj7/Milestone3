from django.urls import include, path
from .views import BalanceLoadView, PortfolioLoadView, ProfitLossView

urlpatterns = [
    path('balance/', BalanceLoadView.as_view(), name='balance_get'),
    path('portfolio/', PortfolioLoadView.as_view(), name="portfolio_get"),
    path('pal/', ProfitLossView.as_view(), name='pal_get'),
]