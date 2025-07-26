from django.urls import include, path
from .views import BalanceLoadView, PortfolioLoadView, ProfitLossView, TopThreeStocksView

urlpatterns = [
    path('balance/', BalanceLoadView.as_view(), name='balance_get'),
    path('portfolio/', PortfolioLoadView.as_view(), name="portfolio_get"),
    path('pal/', ProfitLossView.as_view(), name='pal_get'),
    path('top-stocks/', TopThreeStocksView.as_view(), name='top_stocks_get'),
]