import requests
import json
import datetime
from datetime import *
from nsepython import *
from bsedata.bse import BSE
from bs4 import BeautifulSoup
from django.core import serializers
from .models import Stocksmain, Alertsmain, Categorymain, Journalmain
from django.utils import timezone
from django.utils.timezone import make_aware
from requests import Session
from skpy import Skype
from decouple import config
from dateutil import parser
# from pytz import timezone
import pytz

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
        if val.st_position == "SHORT":
            if val.st_ltp < val.st_buyprice:
                profitStock += 1
            if val.st_ltp > val.st_buyprice:
                lossStock += 1
            if val.st_ltp >= val.st_stoploss:
                attentionStock += 1
            if val.st_ltp <= val.st_targetprice:
                attentionStock += 1
            totalStock += 1
        else:
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
    totalAlert = 0
    attentionAlert = 0
    for val in all_entries:
        if val.al_condition == "IF LTP IS LESS THAN TRIGGER PRICE":
            if val.al_ltp <= val.al_triggerprice:
                attentionAlert = attentionAlert + 1
        elif val.al_condition == "IF LTP IS GREATER THAN TRIGGER PRICE":
            if val.al_ltp >= val.al_triggerprice:
                attentionAlert = attentionAlert + 1
        totalAlert += 1
    data_view = {}
    data_view['totalAlert'] = totalAlert
    data_view['attentionAlert'] = attentionAlert
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

def getAllcategories(userid):
    CategorymainModel_json = serializers.serialize("json", Categorymain.objects.filter(cat_userid = userid).order_by('cat_createdon'))
    json_object = json.loads(CategorymainModel_json)
    return json_object

def getAlljournal(userid, category):
    JournalmainModel_json = serializers.serialize("json", Journalmain.objects.filter(jou_userid = userid, jou_category = category).order_by('jou_buydatetime'))
    json_object = json.loads(JournalmainModel_json)
    for val in json_object:
        buydatetime = convertDatetimetoLocal(val['fields']['jou_buydatetime'])
        selldatetime = convertDatetimetoLocal(val['fields']['jou_selldatetime'])
        val['fields']['rawbuydatetime'] = buydatetime
        val['fields']['buydate'] = buydatetime['date']
        val['fields']['selldate'] = selldatetime['date']
        val['fields']['buytime'] = buydatetime['time']
        val['fields']['selltime'] = selldatetime['time']
    return json_object

def getjournalData(userid, category):
    JournalmainModel_json = serializers.serialize("json", Journalmain.objects.filter(jou_userid = userid, jou_category = category).order_by('jou_buydatetime'))
    json_object = json.loads(JournalmainModel_json)
    total_entries = 0
    inprofit = 0
    inloss = 0
    totalpl = 0
    rdata = {}
    for val in json_object:
        total_entries = total_entries + 1
        totalpl = totalpl + val['fields']['jou_pl']
        if(val['fields']['jou_pl'] > 0):
            inprofit = inprofit + 1
        if(val['fields']['jou_pl'] < 0):
            inloss = inloss + 1
    rdata['total_entries'] = total_entries
    rdata['inprofit'] = inprofit
    rdata['inloss'] = inloss
    rdata['totalpl'] = totalpl
    return rdata

def getAlljournalwithID(userid, id):
    JournalmainModel_json = serializers.serialize("json", Journalmain.objects.filter(jou_userid = userid, id = id).order_by('jou_buydatetime'))
    json_object = json.loads(JournalmainModel_json)
    for val in json_object:
        buydatetime = convertDatetimetoLocal(val['fields']['jou_buydatetime'])
        selldatetime = convertDatetimetoLocal(val['fields']['jou_selldatetime'])
        val['fields']['buydate'] = buydatetime['date']
        val['fields']['selldate'] = selldatetime['date']
        val['fields']['buytime'] = buydatetime['time']

        buy_inputTime = buydatetime['time']
        buy_in_time = datetime.datetime.strptime(buy_inputTime, "%I:%M %p")
        buy_out_time = datetime.datetime.strftime(buy_in_time, "%H:%M")
        val['fields']['24buytime'] = buy_out_time

        sell_inputTime = selldatetime['time']
        sell_in_time = datetime.datetime.strptime(sell_inputTime, "%I:%M %p")
        sell_out_time = datetime.datetime.strftime(sell_in_time, "%H:%M")
        val['fields']['selltime'] = selldatetime['time']
        val['fields']['24selltime'] = sell_out_time
        
        createdOndatetime = convertDatetimetoLocal(val['fields']['jou_createdon'])
        val['fields']['createdondate'] = createdOndatetime['date']
        val['fields']['createdontime'] = createdOndatetime['time']
    return json_object

def convertDatetimetoLocal(rawtime):
    dateformatted = {}
    raw1 = parser.parse(rawtime)
    utc = raw1.replace(tzinfo=pytz.UTC)
    localtz = utc.astimezone(timezone.get_current_timezone())
    dateformatted['date'] = localtz.strftime("%Y-%m-%d")
    dateformatted['time'] = localtz.strftime("%I:%M %p")
    return dateformatted

def timeconvert(str1):
    if str1[-2:] == "AM" and str1[:2] == "12":
        return "00" + str1[2:-2]
    elif str1[-2:] == "AM":
        return str1[:-2]
    elif str1[-2:] == "PM" and str1[:2] == "12":
        return str1[:-2]
    else:
        return str(int(str1[:2]) + 12) + str1[2:8]

def allCategorieswithData(userid):
    data2 = []
    data1 = {}
    totalentries = 0
    in_profit = 0
    in_loss = 0
    total_pl = 0
    all_cat = Categorymain.objects.filter(cat_userid = userid)
    for val in all_cat:
        data1['cat_name'] = val.cat_name
        data1['cat_createdon'] = val.cat_createdon
        all_entries = Journalmain.objects.filter(jou_category = val.cat_name, jou_userid = userid)
        for val1 in all_entries:
            totalentries = totalentries + 1
            total_pl = total_pl + val1.jou_pl
            if(val1.jou_pl > 0):
                in_profit = in_profit + 1
            elif(val1.jou_pl < 0):
                in_loss = in_loss + 1
        data1['total_entries'] = totalentries
        data1['in_profit'] = in_profit
        data1['in_loss'] = in_loss
        data1['total_pl'] = total_pl
        # print(data1)
        data2.append(data1)
        
        totalentries = 0
        in_profit = 0
        in_loss = 0
        total_pl = 0
        data1 = {}
    return data2