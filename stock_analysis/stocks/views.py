# stocks/views.py
import pandas as pd
import pandas_ta as ta
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CSVUploadForm
from .models import StockSymbol, StockPrice, PortfolioEntry
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from django.core.serializers.json import DjangoJSONEncoder
import json

from .models import StockSymbol, StockPrice
from .forms import StockSymbolForm
from .utils import fetch_stock_data, fetch_multiple_stock_data

import csv


def home(request):
    return render(request, 'home.html')

def stock_list(request):
    symbols = StockSymbol.objects.prefetch_related('prices').all()
    print('symbols:', symbols)
    return render(request, 'stocks/stock_list.html', {'symbols': symbols})

from django.core.serializers.json import DjangoJSONEncoder
import json

def stock_detail(request, symbol):
    fetch_stock_data(symbol)  # Ensure data is up to date
    stock = get_object_or_404(StockSymbol, symbol=symbol)
    
    # Fetch portfolio entry
    portfolio_entry = PortfolioEntry.objects.filter(stock=stock).first()

    # Query stock prices for table rendering
    prices = stock.prices.order_by('-date')  # Keep this for templates

    # Convert to DataFrame for TA calculations
    df = pd.DataFrame(list(prices))

        # Ensure data exists before calculations
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])  # Convert date to datetime

        # 🟢 Add Moving Averages (SMA & EMA)
        df['SMA_20'] = ta.sma(df['close_price'], length=20)  # 20-day SMA
        df['EMA_10'] = ta.ema(df['close_price'], length=10)  # 10-day EMA

        # 🔵 Add RSI (Relative Strength Index)
        df['RSI_14'] = ta.rsi(df['close_price'], length=14)  # 14-day RSI

    # Convert data to JSON format for Plotly.js
    technical_data = df.to_json(orient='records', date_format='iso')

    # Query stock prices for candlestick chart
    oldest_prices = stock.prices.order_by('date').values('date', 'open_price', 'high', 'low', 'close_price')  # Keep this for templates

    # Compute average close price
    avg_close_price = prices.aggregate(Avg('close_price'))['close_price__avg']

    # Convert prices to JSON for Plotly
    prices_json = json.dumps(list(prices.values('date', 'close_price')), cls=DjangoJSONEncoder)

    # Convert data to JSON format for JavaScript
    candlestick_data = json.dumps(
        list(oldest_prices.values('date', 'open_price', 'high', 'low', 'close_price')),
        cls=DjangoJSONEncoder
    )

    return render(request, 'stocks/stock_detail.html', {
        'stock': stock,
        'portfolio_entry': portfolio_entry,
        'prices': prices,  # Keep QuerySet for tables
        'avg_close_price': avg_close_price,
        'prices_json': prices_json,  # Pass JSON for visualization
        'technical_data': technical_data,  # Pass JSON data for visualization
        'candlestick_data': candlestick_data  # Pass JSON data for Plotly.js
    })



def add_stock(request):
    if request.method == 'POST':
        form = StockSymbolForm(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['symbol']
            name = form.cleaned_data['name'] 
            fetch_stock_data(symbol)  # Fetch stock data for the input symbol

            # Create stock symbol with manually input name
            StockSymbol.objects.get_or_create(
                symbol=symbol.upper(),
                defaults={'name': name}
            )
            return redirect('stock_list') 
            # return render(request, 'stocks/stock_list.html')  # Redirect to stock list after adding the stock
    else:
        form = StockSymbolForm()

    return render(request, 'stocks/add_stock.html', {'form': form})

# Optional: Add a REST endpoint to return JSON response for stock prices
# def api_stock_data(request, symbol):
#     stock = get_object_or_404(StockSymbol, symbol=symbol)
#     prices = StockPrice.objects.filter(symbol=stock).values('date', 'close_price', 'open_price', 'high', 'low', 'volume')

#     return JsonResponse(list(prices), safe=False)  # Send the data as JSON

def api_stock_data(request, symbol):
    stock = get_object_or_404(StockSymbol.objects.prefetch_related('prices'), symbol=symbol)
    
    # Format data for JSON response
    prices = stock.prices.order_by('-date').values('date', 'close_price', 'open_price', 'high', 'low', 'volume')

    data = {
        "symbol": stock.symbol,
        "name": stock.name,
        "prices": list(prices)  # Convert QuerySet to list for JSON serialization
    }

    return JsonResponse(data, safe=False)  # Send formatted JSON



def delete_stock(request, symbol):
    stock = get_object_or_404(StockSymbol, symbol=symbol)
    if request.method == 'POST':
        stock.delete()  # Delete the stock from the database
        return redirect('stock_list')  # Redirect to stock list after deletion
    return render(request, 'stocks/confirm_delete.html', {'stock': stock})  # Optional confirmation


def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file'].read().decode('utf-8').splitlines()
            reader = csv.DictReader(csv_file)

            # Fix BOM issue
            reader.fieldnames = [field.lstrip('\ufeff') for field in reader.fieldnames]

            for row in reader:
                try:
                    stock_name = row['"Name"'].strip()
                    symbol = row['Symbol'].upper().strip()
                    shares = float(row['Shares (Unit)'])
                    price = float(row['Price ($)'])
                    avg_cost = float(row['Average Cost ($)'])
                    total_return = float(row['Total Return ($)'])
                    equity = float(row['Equity ($)'])
                    gain_since_invested = float(row['Gain Since Invested (%)'])
                    allocation = float(row['Allocation (%)'])

                    stock, created = StockSymbol.objects.get_or_create(
                        symbol=symbol,
                        defaults={'name': stock_name}
                    )

                    # Avoid overwriting existing portfolio entries
                    PortfolioEntry.objects.update_or_create(
                        stock=stock,
                        defaults={
                            'shares': shares,
                            'price': price,
                            'avg_cost': avg_cost,
                            'total_return': total_return,
                            'equity': equity,
                            'gain_since_invested': gain_since_invested,
                            'allocation': allocation,
                        }
                    )

                except Exception as e:
                    print(f"Error processing row: {row} - {e}")  # Log errors for debugging

            return redirect('stock_list')  

    else:
        form = CSVUploadForm()

    return render(request, 'stocks/upload_csv.html', {'form': form})