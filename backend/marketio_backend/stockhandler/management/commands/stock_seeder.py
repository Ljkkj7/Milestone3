from django.core.management.base import BaseCommand
from stockhandler.models import Stock

SAMPLE_STOCKS = [
    {"symbol": "AAPL", "name": "Apple Inc.", "base_price": 175},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "base_price": 2800},
    {"symbol": "TSLA", "name": "Tesla Inc.", "base_price": 700},
    {"symbol": "AMZN", "name": "Amazon.com Inc.", "base_price": 3400},
    {"symbol": "NFLX", "name": "Netflix Inc.", "base_price": 500},
    {"symbol": "MSFT", "name": "Microsoft Corp.", "base_price": 295},
    {"symbol": "NVDA", "name": "NVIDIA Corp.", "base_price": 850},
    {"symbol": "META", "name": "Meta Platforms", "base_price": 320},
]

class Command(BaseCommand):
    help = "Populate the database with sample stock data"

    def handle(self, *args, **kwargs):
        created = 0
        for stock_data in SAMPLE_STOCKS:
            stock, is_created = Stock.objects.get_or_create(
                symbol=stock_data["symbol"],
                defaults={
                    "name": stock_data["name"],
                    "base_price": stock_data["base_price"],
                    "price": stock_data["base_price"],
                }
            )
            if is_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"{created} stocks created."))
