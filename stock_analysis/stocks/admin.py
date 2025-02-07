from django.contrib import admin
from .models import StockSymbol, StockPrice

@admin.register(StockSymbol)
class StockSymbolAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name')

@admin.register(StockPrice)
class StockPriceAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'date', 'open_price', 'close_price')
    list_filter = ('symbol', 'date')
