from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import datetime
from django import template
from django.template import loader
from django.contrib.auth.decorators import login_required
import requests
from decouple import config
import json
from nsepython import *
from django.utils import timezone
from .forms import inputForm
from .models import Stocksmain
from django.utils.timezone import make_aware
from bs4 import BeautifulSoup
from bsedata.bse import BSE
from django.core import serializers
from .functions import nse_livesearch, nse_getPrice, bse_getPrice, bse_livesearch, getAllstocks, updatePrice, stockTrackDashboard

# All the views for stock_track

@login_required(login_url="/login/")
def stock_input(request):
    if request.method == "POST":
        current_user = request.user

        now = datetime.datetime.now()
        aware_datetime = make_aware(now)

        items = Stocksmain(exchange_name = request.POST['exchange-name'], st_name = request.POST['stock-name'], st_code = request.POST['stock-code'], st_buyprice = request.POST['buy-price'], st_targetprice = request.POST['target-price'], st_stoploss = request.POST['stoploss-price'], st_ltp = request.POST['lt-price'], bought_on = request.POST['date'], user_id = current_user.id, last_updated = aware_datetime)

        if (request.POST['exchange-name'] != '' and request.POST['stock-name'] != '' and request.POST['stock-code'] != '' and  request.POST['buy-price'] != '' and request.POST['target-price'] != '' and request.POST['stoploss-price'] != '' and request.POST['lt-price'] != '' and request.POST['date'] != ''):
            context = {'msg': 'Succesfully added '+request.POST['stock-name']+' to database', 'status': 'success', 'segment': 'Add items'}
            # print(items)
            items.save()
        else:
            context = {'msg': 'Please fill all the fields', 'status': 'error', 'segment': 'Add items', 'page' : 'Insert'}
    else:
        context = {'msg': False, 'status': 'error', 'segment': 'Add items', 'page' : 'Insert'}

    html_template = loader.get_template('stocks/stock-input.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def stock_edit(request):
    current_user = request.user
    userid = current_user.id
    all_entries = Stocksmain.objects.filter(user_id = userid)
    context = {'segment': 'Edit items', 'data': all_entries, 'page' : 'Edit'}
    html_template = loader.get_template('stocks/stock-edit.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def nseStockSearch(request):
    if request.method == 'POST':
        que = request.POST.get('que')
        exch = request.POST.get('exchange')
        result = nse_livesearch(que)
        return JsonResponse(result, safe=False)
    else:
        return JsonResponse({'status':'error'})

@login_required(login_url="/login/")
def nseStockPrice(request):
    if request.method == 'POST':
        que = request.POST.get('que')
        result = nse_getPrice(que)
        return JsonResponse(result)
    else:
        return JsonResponse({'price':'0', 'status':'error'})

@login_required(login_url="/login/")
def bseStockPrice(request):
    if request.method == 'POST':
        que = request.POST.get('que')
        result = bse_getPrice(que)
        return JsonResponse(result)
    else:
        return JsonResponse({'price':'0', 'status':'error'})

@login_required(login_url="/login/")
def bseStockSearch(request):
    if request.method == 'POST':
        que = request.POST.get('que')
        exch = request.POST.get('exchange')
        result = bse_livesearch(que)
        return JsonResponse(result, safe=False)
    else:
        return JsonResponse({'status':'error'})

@login_required(login_url="/login/")
def stockDelete(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        result = Stocksmain.objects.filter(id=id).delete()
        # print(result)
        if (result[0] == 1):
            return JsonResponse({'status':'success'})
        else:
            return JsonResponse({'status':'error'})
    else:
        return JsonResponse({'status':'error'})

@login_required(login_url="/login/")
def stock_view(request):
    current_user = request.user
    userid = current_user.id
    data_view = stockTrackDashboard(userid)
    context = {'segment': 'View items', 'data' : data_view, 'page' : 'View'}
    html_template = loader.get_template('stocks/stock-view.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def stocksAll(request):
    if request.method == 'POST':
        # SomeModel_json = serializers.serialize("json", Stocksmain.objects.all())
        current_user = request.user
        userid = current_user.id
        # SomeModel_json = serializers.serialize("json", Stocksmain.objects.filter(user_id = userid).order_by('bought_on'))
        # jsonModel = getAllstocks(userid)
        result = getAllstocks(userid)
        data = {"result": result, "status": "success"}
        return JsonResponse(data)
    else:
        return JsonResponse({'status':'error'})

@login_required(login_url="/login/")
def refreshPrice(request):
    if request.method == 'POST':
        current_user = request.user
        userid = current_user.id
        allStockList = getAllstocks(userid)
        for val in allStockList:
            updatePrice(val['pk'], val['fields']['st_code'], val['fields']['exchange_name'])
        data = {"status": "success"}
        return JsonResponse(data)
    else:
        return JsonResponse({'status':'error'})

@login_required(login_url="/login/")
def stockEdit(request, stock_id):
    current_user = request.user
    userid = current_user.id
    all_entries = Stocksmain.objects.filter(user_id = userid, id = stock_id)
    if request.method == "POST":
        if (request.POST['buy-price'] != '' and request.POST['target-price'] != '' and request.POST['stoploss-price'] != '' and request.POST['lt-price'] != '' and request.POST['date'] != ''):
            db = Stocksmain.objects.get(id = stock_id)
            db.st_buyprice = request.POST['buy-price']
            db.st_targetprice = request.POST['target-price']
            db.st_stoploss = request.POST['stoploss-price']
            db.st_ltp = request.POST['lt-price']
            db.bought_on = request.POST['date']
            db.save()

            context = {'segment': 'Edit items', 'data': all_entries, 'page' : 'Edit', 'msg': 'Succesfully updated data', 'status': 'success'}
        else:
            context = {'segment': 'Edit items', 'data': all_entries, 'page' : 'Edit', 'msg': 'Please fill all the fields', 'status': 'error'}
    else:
        context = {'segment': 'Edit items', 'data': all_entries, 'page' : 'Edit', 'msg': False, 'status': 'error'}
    # print(all_entries)
    html_template = loader.get_template('stocks/stock-single-edit.html')
    return HttpResponse(html_template.render(context, request))