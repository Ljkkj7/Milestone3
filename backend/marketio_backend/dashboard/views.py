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
    
    def get(self, request):
        # Check if requesting another user's portfolio
        target_user_id = request.query_params.get('target_user')
        
        try:
            if target_user_id:
                user_profile = UserProfile.objects.get(user__id=target_user_id)
            else:
                user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            error_msg = "Target user not found." if target_user_id else "User profile not found."
            return Response({"error": error_msg}, status=404)
        
        return self.calculate_portfolio(user_profile)

    def calculate_portfolio(self, user_profile):
        """Helper method to calculate portfolio value"""
        transactions = Transaction.objects.filter(user_profile=user_profile).select_related('stock')
        
        if not transactions.exists():
            return Response({'total_portfolio_value': 0, 'details': []})
        
        # Build portfolio: {symbol: net_quantity}
        portfolio = {}
        
        for tx in transactions:
            symbol = tx.stock.symbol
            portfolio.setdefault(symbol, 0)
            if tx.transaction_type == 'BUY':
                portfolio[symbol] += tx.quantity
            elif tx.transaction_type == 'SELL':
                portfolio[symbol] -= tx.quantity
        
        # Get all stocks for symbols in portfolio (single query)
        symbols_with_quantity = [symbol for symbol, qty in portfolio.items() if qty > 0]
        if not symbols_with_quantity:
            return Response({'total_portfolio_value': 0, 'details': []})
        
        stocks = {stock.symbol: stock for stock in Stock.objects.filter(symbol__in=symbols_with_quantity)}
        
        total_value = 0
        details = []
        
        for symbol, quantity in portfolio.items():
            if quantity <= 0:
                continue
            
            stock = stocks.get(symbol)
            if not stock:
                continue  # Skip if stock not found
            
            stock_value = stock.price * quantity
            total_value += stock_value
            details.append({
                'symbol': symbol,
                'quantity': quantity,
                'current_price': stock.price,
                'value': stock_value
            })
        
        return Response({
            'total_portfolio_value': total_value,
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


class TopThreeStocksView(APIView):
    """
    A view to retrieve the top three stocks by profit/loss for the current user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, req):

        # Check if requesting another user's top stocks
        target_user_id = req.query_params.get('target_user')
        if target_user_id:
            try:
                user_profile = UserProfile.objects.get(user__id=target_user_id)
            except UserProfile.DoesNotExist:
                return Response({"error": "Target user not found."}, status=404)
        else:
            user_profile = UserProfile.objects.get(user=req.user)

        # Get all transactions for the user
        if not user_profile:
            return Response({"error": "User profile not found."}, status=404)
        if not user_profile.user.is_authenticated:
            return Response({"error": "User is not authenticated."}, status=401)
        
        # Get all transactions for the user
        transactions = Transaction.objects.filter(user_profile=user_profile)

        # If no transactions, return empty response
        if not transactions.exists():
            return Response({'top_stocks': []})
        
        # Build portfolio: {symbol: {buy_qty, buy_total, sell_qty, sell_total}}
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

        # Calculate profit/loss for each stock 
        stock_pnl = []
        for symbol, data in portfolio.items():
            net_qty = data['buy_qty'] - data['sell_qty']
            if net_qty <= 0:
                continue  # No holdings, ignore

            try:
                if portfolio[symbol]['sell_total'] - portfolio[symbol]['buy_total'] >= 0:
                    stock_pnl.append({
                        'symbol': symbol,
                        'profit_loss': round(float(portfolio[symbol]['sell_total'] - portfolio[symbol]['buy_total']), 2)
                    })

            except ZeroDivisionError:
                # If there are no buy transactions, skip this stock
                continue

        # Sort by profit/loss and get top three
        top_stocks = sorted(stock_pnl, key=lambda x: x['profit_loss'], reverse=True)[:3]

        return Response({
            'top_stocks': top_stocks
        })