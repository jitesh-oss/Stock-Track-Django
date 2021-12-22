# -*- encoding: utf-8 -*-

from django.urls import path, re_path
from stock_track import views

urlpatterns = [

    path('add/', views.stock_input, name='add'),
    path('edit/', views.stock_edit, name='edit'),
    path('view/', views.stock_view, name='view'),
    path('nse-search/', views.nseStockSearch, name='nse-search'),
    path('bse-search/', views.bseStockSearch, name='bse-search'),
    path('nse-price/', views.nseStockPrice, name='nse-price'),
    path('bse-price/', views.bseStockPrice, name='bse-price'),
    path('stock-delete/', views.stockDelete, name='stock-delete'),
    path('stocks-all/', views.stocksAll, name='stocks-all'),
    path('refresh-price/', views.refreshPrice, name='refresh-price'),
    path('edit/<int:stock_id>/', views.stockEdit, name='stocks-edit'),

]
