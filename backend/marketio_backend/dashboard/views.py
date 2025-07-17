from django.shortcuts import render
from stockhandler.models import Transaction, Stock
from custom_auth.models import UserProfile
from custom_auth.serializers import UserProfileSerializer, TargetUserProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from decimal import Decimal


# Create your views here.


class BalanceLoadView(APIView):
    """
    A view to load a users balance value
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Check if requesting another user's balance
        target_user_id = request.query_params.get('target_user')
        
        if target_user_id:
            try:
                target_user_profile = UserProfile.objects.get(user__id=target_user_id)
                serializer = TargetUserProfileSerializer(target_user_profile)
                return Response(serializer.data)
            except UserProfile.DoesNotExist:
                return Response({"error": "Target user not found."}, status=404)
        else:
            # Get current user's balance
            try:
                balance = UserProfile.objects.get(user=request.user)
                serializer = UserProfileSerializer(balance)
                return Response(serializer.data)
            except UserProfile.DoesNotExist:
                return Response({"error": "User profile not found."}, status=404)


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
    
    def get_target_user_portfolio(self):
        target_user_id = self.request.query_params.get('target_user')
        if not target_user_id:
            return Response({"error": "Target user ID is required."}, status=400)

        try:
            target_user_profile = UserProfile.objects.get(user__id=target_user_id)
            transactions = Transaction.objects.filter(user_profile=target_user_profile)

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
        except UserProfile.DoesNotExist:
            return Response({"error": "Target user not found."}, status=404)


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
                    'buy_total': Decimal(0.0),
                    'sell_qty': 0,
                    'sell_total': Decimal(0.0)
                }
            
            if tx.transaction_type == 'BUY':
                portfolio[symbol]['buy_qty'] += tx.quantity
                portfolio[symbol]['buy_total'] += tx.quantity * tx.price
            elif tx.transaction_type == 'SELL':
                portfolio[symbol]['sell_qty'] += tx.quantity
                portfolio[symbol]['sell_total'] += tx.quantity * tx.price
        
        total_profit_loss = Decimal(0.0)
        details = []

        for symbol, data in portfolio.items():
            net_qty = data['buy_qty'] - data['sell_qty']
            if net_qty <= 0:
                continue  # No holdings, ignore

            try:
                stock = Stock.objects.get(symbol=symbol)
                current_price = stock.price
                avg_buy_price = (data['buy_total'] / Decimal(data['buy_qty'])) if data['buy_qty'] else Decimal("0.0")

                current_value = current_price * Decimal(net_qty)
                cost_basis = avg_buy_price * Decimal(net_qty)
                pnl = current_value - cost_basis
                total_profit_loss += pnl

                details.append({
                    'symbol': symbol,
                    'average_buy_price': round(float(avg_buy_price), 2),
                    'cost_basis': round(float(cost_basis), 2),
                    'current_price': round(float(current_price), 2),
                    'profit_loss': round(float(pnl), 2)
                })

            except Stock.DoesNotExist:
                continue

        return Response({
            'total_profit_loss': round(total_profit_loss, 2),
            'details': details
        })
    