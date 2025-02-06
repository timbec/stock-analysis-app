from django.urls import path
from . import views

urlpatterns = [
    # New path for CSV upload
    path('upload_csv/', views.upload_csv, name='upload_csv'),
    path('add/', views.add_stock, name='add_stock'),
    path('delete/<str:symbol>/', views.delete_stock, name='delete_stock'),
    path('<str:symbol>/', views.stock_detail, name='stock_detail'),
    path('', views.stock_list, name='stock_list'),

]
