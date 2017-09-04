# -*- coding=utf-8 -*-

import requests
import json
import sys
import urllib2
from bs4 import BeautifulSoup
from src.db import stock as Stock
import time, datetime

url = 'http://data.tehir.cn/url/Api/ApiInterface.ashx?flag=stocklist&rows=100&page=%d'


# 公司进本注册资料
# REGISTRATION_URL = "http://soft-f9.eastmoney.com/soft/gp3.php?code=%s02"


def upsert_growth(stock):
    if stock['code'].startswith('30'):
        Stock.find_or_create({'code': stock['code']}, stock)
        print(stock['name'], stock['code'], '-->', stock['area'])


def upsert_all(stock):
    Stock.find_or_create({'code': stock['code']}, stock)


def print_company(rows):
    for stock in rows:
        print(stock)


def total_stock_count():
    response = requests.get('http://data.tehir.cn/url/Api/ApiInterface.ashx?flag=stocklist&rows=1&page=1')
    data = response.text
    data_json = json.loads(data)
    return data_json['total']


def get_stocks(callback):
    total_page = total_stock_count() / 100 + 1
    print('total page > %d' % total_page)
    for i in range(1, total_page + 1):
        response = requests.get(url % i)
        data = response.text
        data_json = json.loads(data)
        th_rows = data_json['rows']
        for stock in th_rows:
            callback(stock)
        sys.stdout.write('request page %d \r' % i)
        sys.stdout.flush()
    print('over')
    print('stock count: %d' % Stock.count())


def print_growth_count():
    print('growth stock count: %d' % Stock.growth_count())


def save_basic_info(code='300692'):
    stock_info_url = 'http://f9.eastmoney.com/sz%s.html' % code

    html = urllib2.urlopen(stock_info_url).read()
    soup = BeautifulSoup(html, "html5lib")
    box_lrs = soup.find_all(class_="box_lr")
    if len(box_lrs) == 0:
        print('没找到数据')
        return
    save_financial_information(code, box_lrs[1].tbody)
    save_equity_structure(code, box_lrs[4].table)
    save_equity_information(code, box_lrs[9].table)
    if len(box_lrs) >= 15:
        save_company_information(code, box_lrs[14].find(class_="box_l").table)


# --东方财富网--
# date 指标名称
# base_earnings_per_share 基本每股收益(元)
# deduct_base_earnings_per_share 扣非每股收益(元)
# attenuation_earnings_per_share 稀释每股收益(元)
# net_profit 净利润(元)
# net_profit_year_on_year_growth 净利润同比增长(%)
# net_profit_rose_growth 净利润滚动环比增长(%)
# weighted_net_worth_yield_rate 加权净资产收益率(%)
# diluted_net_worth_yield_rate 摊薄净资产收益率(%)
# gross_profit_rate 毛利率(%)
# effective_tax_rate 实际税率(%)
# advance_payments_to_operating_receipt 预收款/营业收入
# sales_cash_flow_to_operating_receipt 销售现金流/营业收入
# total_asset_turnover 总资产周转率(次)
# asset_liability_ratio 资产负债率(%)
# current_liabilities_to_total 流动负债/总负债(%)

financial_information_key = [
    'date', 'base_earnings_per_share', 'deduct_base_earnings_per_share', 'attenuation_earnings_per_share',
    'net_profit', 'net_profit_year_on_year_growth', 'net_profit_rose_growth', 'weighted_net_worth_yield_rate',
    'diluted_net_worth_yield_rate', 'gross_profit_rate', 'effective_tax_rate', 'advance_payments_to_operating_receipt',
    'sales_cash_flow_to_operating_receipt', 'total_asset_turnover', 'asset_liability_ratio',
    'current_liabilities_to_total'
]


def save_financial_information(code, information_content):
    if information_content is None:
        print("空重要指标数据："),
        print(code)
        return
    trs = information_content.find_all('tr')
    financial_information1 = {}
    financial_information2 = {}
    for index, row in enumerate(trs):
        tds = row.find_all('td')
        # print(tds[0].get_text())
        financial_information1 = reduce_financial_doc(index, tds[1].get_text(), financial_information1)
        financial_information2 = reduce_financial_doc(index, tds[2].get_text(), financial_information2)
    print(code)
    # print(financial_information1)
    financial_informations = [financial_information1, financial_information2]
    Stock.update({'code': code}, {'$set': {'financial_informations': financial_informations}})


# circulation_A_shares 流通A股
# circulation_A_shares_rate 流通A股比例
# restricted_stock 流通受限股
# total_equity 总股本

def save_equity_structure(code, content_data):
    if content_data is None:
        print("空股本结构数据："),
        print(code)
        return
    equity_structure_content = content_data.tbody
    if equity_structure_content is None:
        print("空股本结构数据"),
        return
    row1 = equity_structure_content.find_all('tr')[1]
    tds1 = row1.find_all('td')
    row2 = equity_structure_content.find_all('tr')[5]
    tds2 = row2.find_all('td')
    row3 = equity_structure_content.find_all('tr')[7]
    tds3 = row3.find_all('td')

    data = {
        "circulation_A_shares": replace_comma(tds1[1].get_text()),
        "circulation_A_shares_rate": pct_to_float(tds1[2].get_text()),

        "restricted_stock": replace_comma(tds2[1].get_text()),
        "restricted_stock_rate": pct_to_float(tds2[2].get_text()),

        "total_equity": replace_comma(tds3[1].get_text()),

    }
    Stock.update({'code': code}, {'$set': data})
    # print(data)


# launch_date 发行日期
# issue_price 发行价格
# issue_shares_number 发行股数
# total_funds_raised 募集资金总额


def save_equity_information(code, content_data):
    if content_data is None:
        print("空新股发行数据："),
        print(code)
        return
    equity_information_content = content_data.tbody
    if equity_information_content is None:
        print("空新股发行数据："),
        print(code)
        return
    row1 = equity_information_content.find_all('tr')[1]
    tds = row1.find_all('td')
    data = {
        "launch_date": str_to_date(tds[0].get_text()),
        "issue_price": try_float(tds[1].get_text()),
        "issue_shares_number": replace_comma(tds[2].get_text()),
        "total_funds_raised": replace_comma(tds[3].get_text()),
    }
    # print(row1)
    Stock.update({'code': code}, {'$set': data})
    # print(data)


# full_name 公司全名
# legal_representative 法人代表
# registered_address 注册地址
# registered_capital 注册资金

def save_company_information(code, content_data):
    if content_data is None:
        print("空公司信息数据："),
        print(code)
        return
    company_information_content = content_data.tbody
    if company_information_content is None:
        print("空公司信息数据："),
        print(code)
        return
    trs = company_information_content.find_all('tr')
    row0 = trs[0]
    tds0 = row0.find_all('td')
    row1 = trs[1]
    tds1 = row1.find_all('td')
    row2 = trs[2]
    tds2 = row2.find_all('td')

    data = {
        "full_name": tds0[1].get_text(),
        "legal_representative": tds0[3].get_text(),
        "registered_address": tds1[1].get_text(),
        "registered_capital": unit_to_number(tds1[3].get_text()),
        "establishment_at": str_to_date(tds2[1].get_text()),
        "launch_date": str_to_date(tds2[3].get_text()),
    }
    Stock.update({'code': code}, {'$set': data})
    # print(data)


def str_to_date(value):
    # print(value)
    if value == '--':
        return None
    t = time.strptime(value, "%Y-%m-%d")
    y, m, d = t[0:3]
    return datetime.datetime(y, m, d)


def save_all_basic_info():
    stocks = Stock.find().sort('code', -1)
    for stock in stocks:
        save_basic_info(stock['code'])


def reduce_financial_doc(index, value, financial_information={}):
    financial_information[financial_information_key[index]] = unit_to_number(value)
    return financial_information


def unit_to_number(value):
    value = value.encode('utf8')
    if value.find("万") >= 0:
        value = value.replace("万", "")
        return float_or_str(value) * 10000
    elif value.find("亿") >= 0:
        value = value.replace("亿", "")
        return float_or_str(value) * 100000000
    elif value == '--':
        return None
    else:
        return float_or_str(value)


def replace_comma(value):
    try:
        value = value.replace(",", "")
        return float(value)
    except ValueError:
        return None


def try_float(value):
    try:
        return float(value)
    except ValueError:
        return None


def try_int(value):
    try:
        return int(value)
    except ValueError:
        return None


def pct_to_float(value):
    return try_float(value.split('%')[0])


def float_or_str(value):
    try:
        value = float(value)
        return round(value, 2)
    except ValueError:
        return value


# up_down: 涨跌金额, up_down_pct: 涨跌百分比, swing: 振幅, turnover: 成交量, trading_volume: 成交金额,today_start:
def save_stock(item):
    values = item.split(',')
    data = {'code': values[1], 'name': values[2], 'price': try_float(values[3]), 'up_down': try_float(values[4]),
            'up_down_pct': pct_to_float(values[5]), 'swing': pct_to_float(values[6]),
            'turnover': try_int(values[7]), 'trading_volume': try_int(values[8]),
            'yesterday_price': try_float(values[9]), 'today_start': try_float(values[10]),
            'today_highest': try_float(values[11]), 'today_lowest': try_float(values[12])}
    Stock.find_or_create({'code': values[1]}, data)


def get_growth_list(page=1):
    print('page>> %d' % page)
    growth_stock_list_url = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C.80&sty=FCOIATA&sortType=C&sortRule=-1&page=%s&pageSize=%s&quote=&token=7bc05d0d4c3c22ef9fca8c2a912d779c'
    per_page = 100
    url_with_page = growth_stock_list_url % (page, per_page)
    data = requests.get(url_with_page).text
    data = data.encode('utf8')
    rows = data.split('\",\"')
    before_stock = rows.pop(0)
    stock1 = before_stock.split('\"')[1]
    rows.append(stock1)
    end_stock = rows.pop(-1)
    stock2 = end_stock.split('\"')[0]
    rows.append(stock2)
    for item in rows:
        save_stock(item)
