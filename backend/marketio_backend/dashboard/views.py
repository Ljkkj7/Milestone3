from django.shortcuts import render
from stockhandler.models import Transaction, Stock
from custom_auth.models import UserProfile
from custom_auth.serializers import UserProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.


class BalanceLoadView(APIView):
    """
    A view to load a users balance value
    """

    permission_classes = [IsAuthenticated]

    def get(self, req):
        balance = UserProfile.objects.get(user=req.user)
        serializer = UserProfileSerializer(balance)
        return Response(serializer.data)


class PortfolioLoadView(APIView):
    """
    A view to load a users portfolio value
    """
    permission_classes = [IsAuthenticated]

    def get(self, req):
        user_profile = UserProfile.objects.get(user=req.user)
        transactions = Transaction.objects.filter(user_profile=user_profile)

        if not transactions.exists():
            return Response({'total_portfolio_value': 0})
        
        # Build portfolio: {symbol: net_Quantity}
        portfolio = {}

        for tx in transactions:
            symbol = tx.stock.symbol
            portfolio.setdefault(symbol, 0)
            if tx.transaction_type == 'BUY':
                portfolio[symbol] += tx.quantity
            elif tx.transaction_type == 'SELL':
                portfolio[symbol] -= tx.quantity
        
        totalValue = 0
        details = []

        for symbol, quantity in portfolio.items():
            if quantity <= 0:
                continue
            try:
                stock = Stock.objects.get(symbol=symbol)
                stockValue = stock.price * quantity
                totalValue += stockValue
                details.append({
                    'symbol': symbol,
                    'quantity': quantity,
                    'current_price': stock.price,
                    'value': stockValue
                })
            except Stock.DoesNotExist:
                continue
        
        return Response({
            'total_portfolio_value': totalValue,
            'details': details
        })

class ProfitLossView(APIView):
    """
    A view to calculate the current P&L of a users stock
    """

    permission_classes = [IsAuthenticated]

    def get(self, req):
        user_profile = UserProfile.objects.get(user=req.user)
        transactions = Transaction.objects.filter(user_profile=user_profile)

        if not transactions.exists():
            return Response({'total_profit_loss': 0, 'details': []})
        
        portfolio = {}
        for tx in transactions:
            if not tx.stock:
                continue
            
            symbol = tx.stock.symbol
            if symbol not in portfolio:
                portfolio[symbol] = {
                    'buy_qty': 0,
                    'buy_total': 0.0,
                    'sell_qty': 0,
                    'sell_total': 0.0
                }
            
            if tx.transaction_type == 'BUY':
                portfolio[symbol]['buy_qty'] += tx.quantity
                portfolio[symbol]['buy_total'] += tx.quantity * tx.price
            elif tx.transaction_type == 'SELL':
                portfolio[symbol]['sell_qty'] += tx.quantity
                portfolio[symbol]['sell_total'] += tx.quantity * tx.price
        
        total_profit_loss = 0.0
        details = []

        for symbol, data in portfolio.items():
            net_qty = data['buy_qty'] - data['sell_qty']
            if net_qty <= 0:
                continue  # No holdings, ignore

            try:
                stock = Stock.objects.get(symbol=symbol)
                current_price = stock.price
                avg_buy_price = data['buy_total'] / data['buy_qty'] if data['buy_qty'] else 0

                current_value = current_price * net_qty
                cost_basis = avg_buy_price * net_qty
                pnl = current_value - cost_basis

                total_profit_loss += pnl

                details.append({
                    'symbol': symbol,
                    'average_buy_price': round(avg_buy_price, 2),
                    'cost_basis': round(cost_basis, 2),
                    'profit_loss': round(pnl, 2)
                })

            except Stock.DoesNotExist:
                continue

        return Response({
            'total_profit_loss': round(total_profit_loss, 2),
            'details': details
        })
    