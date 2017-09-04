from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client.spider

stocks = db.stocks


def find_or_create(criteria, stock):
    stocks.update(criteria, {'$set': stock}, True)


def update(criteria, stock):
    stocks.update_one(criteria, stock)


def count():
    return stocks.count()


def growth_count():
    return stocks.count({'code': r'^30(.*?)'})


def find(query={}):
    return stocks.find(query)
