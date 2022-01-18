import requests
import json
import datetime
from datetime import date
from datetime import datetime
from nsepython import *
from bsedata.bse import BSE
from bs4 import BeautifulSoup
from django.core import serializers
from .models import Stocksmain, Alertsmain
from django.utils import timezone
from django.utils.timezone import make_aware
from requests import Session
from skpy import Skype
from decouple import config

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

def fut_getPrice(que):
    # r = nse_fno(que)["underlyingValue"]
    r = nse_quote_ltp(que,"latest","Fut")
    result = {'price': r, 'status':200}
    return result

def fut_getPrice1(que):
    page_url = "https://www.nseindia.com/get-quotes/derivatives?symbol="+que
    chart_data_url = "https://www.nseindia.com/api/chart-databyindex"

    date_input = expiry_list(que)[0]
    datetime_object = datetime.datetime.strptime(date_input, "%d-%b-%Y")
    expiry_date = datetime_object.strftime("%d-%m-%Y")

    s = Session()
    h = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    }
    s.headers.update(h)
    r = s.get(page_url)
    data = {"index": "FUTSTK"+que+expiry_date+"XX0.00"}
    r = s.get(chart_data_url, params=data)
    data = r.json()['grapthData']
    price = data[len(data)-1][1]
    result = {'price': price, 'status':200}
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

def getAllstocks_all():
    StocksmainModel_json = serializers.serialize("json", Stocksmain.objects.filter().order_by('bought_on'))
    json_object = json.loads(StocksmainModel_json)
    return json_object

def updatePrice(id, code, exchange, st_type):
    price1 = 0
    now = datetime.datetime.now()
    current_datetime = make_aware(now)
    if st_type == 'DERIVATIVE':
        price1 = fut_getPrice(code)["price"]
    else:
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

def message_skype(st_message):
    sk = Skype(config('SKYPE_UID'), config('SKYPE_PWD'))
    sk.user
    sk.contacts
    sk.chats
    ch = sk.contacts[config('SKYPE_TO')].chat
    ch.sendMsg(st_message)

def checkStatus(st_code, st_name, st_exchange, st_type, st_ltp, st_buy, st_target, st_stoploss):
    # message_skype("SUP")
    if st_ltp >= st_target:
        profit = st_ltp-st_buy
        message_skype("Target Achieved for "+st_name+"("+st_code+") - ("+st_exchange+") - ("+st_type+") : Total Profit Per Share = "+str(profit)+" | Buy: "+str(st_buy)+", LTP: "+str(st_ltp)+", TG: "+str(st_target))
    elif st_ltp <= st_stoploss:
        loss = st_buy-st_ltp
        message_skype("Stoploss hit for "+st_name+"("+st_code+") - ("+st_exchange+") - ("+st_type+") : Total Loss Per Share = "+str(loss)+" | Buy: "+str(st_buy)+", LTP: "+str(st_ltp)+", SL: "+str(st_stoploss))

def alertDashboard(userid):
    all_entries = Alertsmain.objects.filter(al_user_id = userid)
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

def getAllalerts(userid):
    AlertsmainModel_json = serializers.serialize("json", Alertsmain.objects.filter(al_user_id = userid).order_by('al_last_updated'))
    json_object = json.loads(AlertsmainModel_json)
    return json_object

def updateAlert(id, code, exchange, altype):
    price1 = 0
    now = datetime.datetime.now()
    current_datetime = make_aware(now)
    if altype == 'DERIVATIVE':
        price1 = fut_getPrice(code)["price"]
    else:
        if exchange == 'NSE':
            price1 = nse_getPrice(code)['price']
        elif exchange == 'BSE':
            price1 = bse_getPrice(code)['price']

    alert = Alertsmain.objects.get(pk=id)
    alert.al_ltp = price1
    alert.al_last_updated = current_datetime
    alert.save()

def getAllalerts_all():
    AlertsmainModel_json = serializers.serialize("json", Alertsmain.objects.filter().order_by('al_last_updated'))
    json_object = json.loads(AlertsmainModel_json)
    return json_object

def checkAlertStatus(al_code, al_name, al_exchange, al_type, al_ltp, al_condition, al_trigger, al_note):
    # message_skype("SUP")
    if al_condition == "IF LTP IS LESS THAN TRIGGER PRICE":
        if al_ltp <= al_trigger:
            message = "Your alert for "+al_name+"("+al_code+") - ("+al_exchange+")("+al_type+") has been triggered since LTP:"+str(al_ltp)+" is less than "+str(al_trigger)+" with Note: "+al_note
            message_skype(message)
    elif al_condition == "IF LTP IS GREATER THAN TRIGGER PRICE":
        if al_ltp >= al_trigger:
            message = "Your alert for "+al_name+"("+al_code+") - ("+al_exchange+")("+al_type+") has been triggered since LTP:"+str(al_ltp)+" is greater than "+str(al_trigger)+" with Note: "+al_note
            message_skype(message)