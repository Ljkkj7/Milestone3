from django.db import models
from django.contrib.auth.models import User
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

    def simulate_price_change(self):
        """"Simulate a price change based on a sine wave function and random noise."""
        now = timezone.now()
        delta = (now - self.created_at).total_seconds() / 3600 # Convert to hours
        amplitude = 10

        wave = amplitude * math.sin(0.05*delta + 2*math.pi*0.5)

        noise = random.uniform(-1.0, 1.0)

        new_price = Decimal(self.base_price) + Decimal(wave + noise)
        self.price = round(new_price, 2)
        self.save()

