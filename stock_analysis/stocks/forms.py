# stocks/forms.py
from django import forms

class StockSymbolForm(forms.Form):
    name = forms.CharField(label='Company Name', max_length=100)
    symbol = forms.CharField(label='Stock Symbol', max_length=10)
    

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV")