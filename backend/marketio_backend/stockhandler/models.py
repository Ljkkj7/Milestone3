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

        #Flag to indicate a market event
        if self.status != "positive":
            self.status = "positive"

        severity = random.randint(1, 10)  # Random severity level
        event_impact = severity * float(self.amplitude) # Impact based on severity and amplitude

        # Simulate a sine wave effect with random noise
        stock_impact = random.uniform(0.5, event_impact)
        noise = random.uniform(-float(self.noise), float(self.noise))
        wave = stock_impact * math.sin(0.05 * timezone.now().timestamp() + 2 * math.pi * 0.5)

        # Calculate new price
        new_price = Decimal(self.price) + Decimal(wave + noise)
        self.price = max(Decimal('0.01'), Decimal(round(new_price, 2)))  # Ensure price doesn't go below 0.01

        # Save the updated stock price
        self.save()

    def simulate_negative_market_event(self):
        """Simulate a market event that affects the stock price negatively."""

        #Flag to indicate a market event
        if self.status != "negative":
            self.status = "negative" 

        severity = random.randint(1, 10)  # Random severity level
        event_impact = severity * float(self.amplitude)  # Impact based on severity and amplitude

        # Simulate a sine wave effect with random noise
        stock_impact = -abs(random.uniform(0.5, event_impact))
        noise = random.uniform(-float(self.noise), float(self.noise))
        wave = stock_impact * math.sin(0.05 * timezone.now().timestamp() + 2 * math.pi * 0.5)

        # Calculate new price
        new_price = Decimal(self.price) - Decimal(wave + noise)
        self.price = max(Decimal('0.01'), Decimal(round(new_price, 2)))  # Ensure price doesn't go below 0.01

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
