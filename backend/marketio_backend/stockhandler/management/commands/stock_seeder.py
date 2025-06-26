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
    {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "base_price": 160},
    {"symbol": "BAC", "name": "Bank of America Corp.", "base_price": 35},
    {"symbol": "XOM", "name": "Exxon Mobil Corp.", "base_price": 110},
    {"symbol": "CVX", "name": "Chevron Corp.", "base_price": 165},
    {"symbol": "WMT", "name": "Walmart Inc.", "base_price": 145},
    {"symbol": "PG", "name": "Procter & Gamble Co.", "base_price": 150},
    {"symbol": "UNH", "name": "UnitedHealth Group Inc.", "base_price": 490},
    {"symbol": "V", "name": "Visa Inc.", "base_price": 230},
    {"symbol": "MA", "name": "Mastercard Inc.", "base_price": 375},
    {"symbol": "DIS", "name": "The Walt Disney Co.", "base_price": 105},
    {"symbol": "INTC", "name": "Intel Corp.", "base_price": 34},
    {"symbol": "CSCO", "name": "Cisco Systems Inc.", "base_price": 50},
    {"symbol": "ADBE", "name": "Adobe Inc.", "base_price": 550},
    {"symbol": "PFE", "name": "Pfizer Inc.", "base_price": 40},
    {"symbol": "MRNA", "name": "Moderna Inc.", "base_price": 120},
    {"symbol": "ORCL", "name": "Oracle Corp.", "base_price": 130},
    {"symbol": "CRM", "name": "Salesforce Inc.", "base_price": 220},
    {"symbol": "T", "name": "AT&T Inc.", "base_price": 16},
    {"symbol": "KO", "name": "Coca-Cola Co.", "base_price": 60},
    {"symbol": "PEP", "name": "PepsiCo Inc.", "base_price": 180},
    {"symbol": "NKE", "name": "Nike Inc.", "base_price": 100},
    {"symbol": "SBUX", "name": "Starbucks Corp.", "base_price": 95},
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
