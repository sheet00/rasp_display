import os
import random

import time
import board
import adafruit_dht
from datetime import datetime, timedelta
from pytz import timezone
from dateutil import parser

import requests
from bs4 import BeautifulSoup

import pymysql.cursors
import json
from decimal import Decimal


def main():
    os.chdir("/home/pi/rasp_display")

    template_str = get_template()

    # dht
    dht = get_dht()

    # weather
    w_str = get_weather()

    # news
    news = get_news()

    # graph
    data = select_temp_minutes()

    js = '''
    <script>
  document.addEventListener("DOMContentLoaded", function(event) {
    main.init();
  });
    </script>
        '''

    # params
    dict = {
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'js': js,
        'temp': dht['temp'],
        'hum': dht['hum'],
        'weather': w_str,
        'news_title': news['title'],
        'news_desc': news['desc'],
        'json_temps': data['temps'],
        'json_hums': data['hums'],
        'json_created_at': data['created_at']
    }

    print(dht)
    template_str = template_str.format(**dict)

    output_html(template_str)


def get_template():
    with open('template.html', mode='r') as f:
        s = f.read()
        return s


def output_html(template_str):
    with open('output.html', mode='w') as f:
        f.write(template_str)


def get_dht():
    # 接続したGPIOポート:22
    dhtDevice = adafruit_dht.DHT22(board.D22)

    #Simple test — Adafruit CircuitPython DHT Library 1.0 documentation https://docs.circuitpython.org/projects/dht/en/latest/examples.html#id1
    is_success = False
    while is_success == False:
        try:
            #測定開始
            t = dhtDevice.temperature
            h = dhtDevice.humidity
            is_success = True

        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error



    r = {"temp": t, "hum": h}

    if h is not None:
        r['temp'] = round(r['temp'], 2)
        r['hum'] = round(r['hum'], 2)

    return r


def get_weather():
    url = 'https://weathernews.jp/onebox/35.914133/140.077946/q=%E8%8C%A8%E5%9F%8E%E7%9C%8C%E5%8F%96%E6%89%8B%E5%B8%82&v=c52280f1ddc0f37fe5624a2e512990048af611693d6bc8f26e3d1502ed5c3faf&temp=Temp.c&lang=ja'
    r = requests.get(url)

    soup = BeautifulSoup(r.text, "lxml")
    title = soup.find("h1", attrs={"class": "index__tit"})
    body = soup.find(
        "div", attrs={"class": "wx__table act"}
        )

    str = body.prettify()
    # str = str.replace('//smtgvs', 'https://smtgvs')
    # str = str.replace('//weathernews.jp', 'https://weathernews.jp')

    return str


def get_news():
    urls = ["https://www.nhk.or.jp/rss/news/cat0.xml",
            "https://www.nhk.or.jp/rss/news/cat1.xml"]

    news_list = []
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        soup = soup.find_all("item")

        news_list += soup

    jp = timezone('Asia/Tokyo')
    from_date = datetime.now(jp) - timedelta(days=1)
    recent_news_list = []
    for news in news_list:
        pub_date = parser.parse(news.pubdate.text).astimezone(jp)
        if from_date < pub_date:
            recent_news_list.append(news)

    select_news = random.choice(recent_news_list)
    r = {'title': select_news.title.text, 'desc': select_news.description.text}
    return r


def decimal_default_proc(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def select_temp_minutes():
    conn = get_connect()

    try:
        with conn.cursor() as cursor:
            sql = "select * from temp_minutes;"
            cursor.execute(sql)

            results = cursor.fetchall()

            created_at = []
            temps = []
            hums = []
            for row in results:
                created_at.append(row['created_at'].strftime('%H:%M'))
                temps.append(row['temp'])
                hums.append(row['hum'])

            data = {
                'created_at': json.dumps(created_at),
                'temps': json.dumps(temps, default=decimal_default_proc),
                'hums': json.dumps(hums, default=decimal_default_proc)
            }

            return data
    finally:
        conn.close()


def get_connect():
    conn = pymysql.connect(host=os.environ.get('DB_HOST'),
                           user=os.environ.get('DB_USER'),
                           password=os.environ.get('DB_PASSWORD'),
                           db=os.environ.get('DB_NAME'),
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

    return conn


main()
