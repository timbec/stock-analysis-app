# stocks/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CSVUploadForm
from .models import StockSymbol, StockPrice, PortfolioEntry
from django.db.models import Avg
from django.http import JsonResponse

from django.core.serializers.json import DjangoJSONEncoder
import json

from .forms import StockSymbolForm
from .utils import fetch_stock_data, fetch_multiple_stock_data

import csv




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

    # Compute average close price
    avg_close_price = prices.aggregate(Avg('close_price'))['close_price__avg']

    # Convert prices to JSON for Plotly
    prices_json = json.dumps(list(prices.values('date', 'close_price')), cls=DjangoJSONEncoder)

    return render(request, 'stocks/stock_detail.html', {
        'stock': stock,
        'portfolio_entry': portfolio_entry,
        'prices': prices,  # Keep QuerySet for tables
        'avg_close_price': avg_close_price,
        'prices_json': prices_json  # Pass JSON for visualization
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