import requests

lines = open("../sources/stock_curl.txt", "r").readlines()

for line in lines:
    url = line.split('\'')[1]
    if url.startswith('http') and not url.endswith(('.jpg', '.css')) \
            and not ('.html' in url) \
            and not ('.js' in url) \
            and not ('.png' in url) \
            and not ('.gif' in url) \
            and not ('imageType' in url) \
            and not ('avator' in url):
        response = requests.get(url)
        if '300688' in response.text \
                and '300691' in response.text:
            print('iiiiiiiii')
            print(url)
            print(response.text)


