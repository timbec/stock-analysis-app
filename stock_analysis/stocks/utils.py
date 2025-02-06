# stocks/utils.py
import yfinance as yf
from django.db.models import F 
from .models import StockSymbol, StockPrice
from datetime import datetime
from django.db import IntegrityError


def fetch_multiple_stock_data(symbols):
    for symbol in symbols:
        fetch_stock_data(symbol)

def fetch_stock_data(symbol):
    stock_data = yf.download(symbol, period='1y')
    # print('Line 15: stock_data:', stock_data)
    
    ticker = yf.Ticker(symbol)
    company_name = ticker.info.get('shortName', symbol) 
    if stock_data.empty:
        print(f"No data found for symbol: {symbol}")
        return
    try:
        # Get or create the stock symbol in the database
        stock, created = StockSymbol.objects.get_or_create(
        symbol=symbol.upper(), 
        defaults={'name': company_name})
        if created:
            print(f"Created new StockSymbol for {symbol}")
        else:
            print(f"StockSymbol for {symbol} already exists")

        # Store the stock prices
        for date, row in stock_data.iterrows():
            StockPrice.objects.update_or_create(
                symbol=stock,
                date=date.date(),  # Date from index
                defaults={
                    'open_price': row['Open'],
                    'close_price': row['Close'],
                    'high': row['High'],
                    'low': row['Low'],
                    'volume': row['Volume'],
                }
            )
    except IntegrityError as e:
        print(f"IntegrityError: {e}")


def update_stock_names():
    # Get all StockSymbol entries that don't have a name or have the symbol as the name
    stocks_to_update = StockSymbol.objects.filter(name__exact=F('symbol'))

    for stock in stocks_to_update:
        ticker = yf.Ticker(stock.symbol)
        company_name = ticker.info.get('shortName', stock.symbol)  # Fetch the company name or default to symbol
        stock.name = company_name  # Update the name
        stock.save()  # Save the updated record
        print(f"Updated {stock.symbol} with name {company_name}")

