from django.db import models
from django.contrib.auth.models import User
from custom_auth.models import UserProfile
import math
import random
from decimal import Decimal
from django.utils import timezone


# Create your models here.

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    created_at = models.DateTimeField(auto_now_add=True)
    amplitude = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    noise = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    status = models.CharField(max_length=20, default="normal")

    def simulate_price_change(self):
        """"Simulate a price change based on a sine wave function and random noise."""

        #Check if a market event is happening to this stock
        if self.status == "positive":
            self.simulate_positive_market_event()
            return

        if self.status == "negative":
            self.simulate_negative_market_event()
            return

        now = timezone.now()
        delta = (now - self.created_at).total_seconds() / 3600 # Convert to hours
        amplitude = 10

        wave = amplitude * math.sin(0.05*delta + 2*math.pi*0.5)

        noise = random.uniform(-1.0, 1.0)

        new_price = Decimal(self.base_price) + Decimal(wave + noise)
        self.price = round(new_price, 2)
        self.save()

    def simulate_positive_market_event(self):
        """Simulate a market event that affects the stock price positively."""
        
        # Set status to positive if not already
        if self.status != "positive":
            self.status = "positive"

        # MASSIVE amplification for dramatic price swings
        severity = random.randint(8, 10)  # Higher severity (8-10 instead of 1-10)
        
        # Hugely amplified event impact - multiply by 50-100x instead of just amplitude
        base_multiplier = random.uniform(50.0, 100.0)  # Massive base multiplier
        event_impact = severity * float(self.amplitude) * base_multiplier
        
        # Much larger stock impact range for dramatic swings
        stock_impact = random.uniform(20.0, event_impact)  # Start from 20 instead of 0.5
        
        # Amplified noise for more volatility
        noise = random.uniform(-float(self.noise) * 10, float(self.noise) * 10)
        
        # sine wave much more aggressive
        # Faster frequency (0.5 instead of 0.05) and bigger amplitude
        time_factor = 0.5 * timezone.now().timestamp()
        wave = stock_impact * math.sin(time_factor + 2 * math.pi * 0.5)

        # Calculate new price - this can now create 300-400% swings
        price_change = wave + noise
        new_price = Decimal(self.price) + Decimal(price_change)
        
        self.price = max(Decimal('0.01'), Decimal(round(new_price, 2)))
            
        # Save the updated stock price
        self.save()

    def simulate_negative_market_event(self):
        """Simulate a market event that affects the stock price negatively."""
        
        # Set status to negative if not already
        if self.status != "negative":
            self.status = "negative"

        # MASSIVE amplification for dramatic price crashes
        severity = random.randint(8, 10)  # Higher severity (8-10 instead of 1-10)
        
        # Hugely amplified event impact - multiply by 30-80x for crashes
        base_multiplier = random.uniform(30.0, 80.0)  # Large but slightly less than positive
        event_impact = severity * float(self.amplitude) * base_multiplier

        # Much larger negative stock impact range
        stock_impact = -abs(random.uniform(15.0, event_impact))  # Start from 15 instead of 0.5
        
        # Amplified noise for more volatility
        noise = random.uniform(-float(self.noise) * 10, float(self.noise) * 10)
        
        # Keep your sine wave but make it much more aggressive for crashes
        # Faster frequency and bigger amplitude for dramatic drops
        time_factor = 0.5 * timezone.now().timestamp()
        wave = stock_impact * math.sin(time_factor + 2 * math.pi * 0.5)

        # Calculate new price
        price_change = wave + noise
        new_price = Decimal(self.price) + Decimal(price_change)
        
        self.price = max(Decimal('0.01'), Decimal(round(new_price, 2)))
        
            
        # Save the updated stock price
        self.save()

    def market_event_end(self):
        """Helper method to reset bool states on stocks"""

        self.status = "normal"

        self.save()

class Transaction(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=4, choices=[('BUY', 'Buy'), ('SELL', 'Sell')])
