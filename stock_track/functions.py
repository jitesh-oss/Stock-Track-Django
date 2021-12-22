import requests
import json
import datetime
from nsepython import *
from bsedata.bse import BSE
from bs4 import BeautifulSoup
from django.core import serializers
from .models import Stocksmain
from django.utils import timezone
from django.utils.timezone import make_aware

def nse_livesearch(que):
    url = "https://www.nseindia.com/api/search/autocomplete?q="+que
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
    }
    response = requests.request("GET", url, headers=headers)
    json_object = json.loads(response.text)
    raw_res = []
    for i in range(len(json_object['symbols'])):
        raw_res.append(json_object['symbols'][i])
    return raw_res

def nse_getPrice1(que):
    url = "https://www.nseindia.com/api/quote-equity"
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Host': 'www.nseindia.com',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Sec-GPC': '1',
        'TE': 'trailers',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
    }
    PARAMS = {'symbol':que}
    response = requests.get( url, headers=headers, params = PARAMS)
    # print(response.status_code)
    if response.status_code == 200:
        json_object = json.loads(response.text)
        result = json_object['priceInfo']['lastPrice']
        return {'price':result, 'status': 200}
    else:
        result = response.status_code
        return {'price':'0', 'status': result}

def nse_getPrice(que):
    r = nse_eq(que)['priceInfo']['lastPrice']
    result = {'price':r, 'status':200}
    return result

def bse_getPrice(que):
    b = BSE()
    q = b.getQuote(que)
    r = q['currentValue']
    result = {'price':r, 'status':200}
    return result

def bse_livesearch(que):
    url = "https://api.bseindia.com/Msource/1D/getQouteSearch.aspx?Type=EQ&text="+que+"&flag=nw"
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
    }
    response = requests.request("GET", url, headers=headers)
    # json_object = json.loads(response.text)
    parsed_html = BeautifulSoup(response.text, 'html.parser')
    raw_res = []
    for content in parsed_html.find_all('li'):
        res1 = content.a.span.text
        res2 = res1.split()
        raw_res.append(res2)
    return raw_res

def getAllstocks(userid):
    StocksmainModel_json = serializers.serialize("json", Stocksmain.objects.filter(user_id = userid).order_by('bought_on'))
    json_object = json.loads(StocksmainModel_json)
    return json_object

def updatePrice(id, code, exchange):
    price1 = 0
    now = datetime.datetime.now()
    current_datetime = make_aware(now)
    if exchange == 'NSE':
        price1 = nse_getPrice(code)['price']
    elif exchange == 'BSE':
        price1 = bse_getPrice(code)['price']

    stock = Stocksmain.objects.get(pk=id)
    stock.st_ltp = price1
    stock.last_updated = current_datetime
    stock.save()

def stockTrackDashboard(userid):
    all_entries = Stocksmain.objects.filter(user_id = userid)
    totalStock = 0
    profitStock = 0
    lossStock = 0
    attentionStock = 0
    for val in all_entries:
        if val.st_ltp > val.st_buyprice:
            profitStock += 1
        if val.st_ltp < val.st_buyprice:
            lossStock += 1
        if val.st_ltp <= val.st_stoploss:
            attentionStock += 1
        if val.st_ltp >= val.st_targetprice:
            attentionStock += 1
        totalStock += 1
    data_view = {}
    data_view['total'] = totalStock
    data_view['profit'] = profitStock
    data_view['loss'] = lossStock
    data_view['attention'] = attentionStock
    return data_view