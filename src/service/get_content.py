from bs4 import BeautifulSoup

import requests 

html = requests.get('http://www.jianshu.com').content

soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')

result = soup('div')

print result


