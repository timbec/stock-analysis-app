from django.db import models
from django.utils.timezone import now

class StockSymbol(models.Model):
    ##Ensure each symbol is unique
    symbol = models.CharField(max_length=10, unique=True) 
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)  # Track when stock was added

    def __str__(self):
        return f"{self.name} ({self.symbol})"

class StockPrice(models.Model):
    symbol = models.ForeignKey(StockSymbol, on_delete=models.CASCADE, related_name='prices')  # Use symbol)
    date = models.DateField(db_index=True)  # Add an index on the date field for faster queries
    open_price = models.FloatField()
    close_price = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    volume = models.BigIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)  # Track when price was added

    class Meta:
        unique_together = ('symbol', 'date')

    def __str__(self):
        return f"{self.symbol.symbol} on {self.date}"


class PortfolioEntry(models.Model):
    stock = models.ForeignKey(StockSymbol, on_delete=models.CASCADE)
    shares = models.FloatField()  # Number of shares you hold
    price = models.FloatField()  # Price per share when purchased
    avg_cost = models.FloatField()  # Average cost per share
    total_return = models.FloatField()  # Total return in dollars
    equity = models.FloatField()  # Equity value (total value of holdings)
    gain_since_invested = models.FloatField()  # Gain since initial investment
    allocation = models.FloatField()  # Percentage allocation of your portfolio
    created_at = models.DateTimeField(auto_now_add=True)  # Track when entry was added
    updated_at = models.DateTimeField(auto_now=True)  # Track last modification


    def __str__(self):
        return f"{self.stock.symbol} - {self.shares} shares"