from flask import Flask, render_template
import os
import pymysql
import requests
from icecream import ic
import datetime

app = Flask(__name__, static_folder='static')


def get_dht():
    """
    部屋の温度取得
    """
    conn = pymysql.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        db=os.environ.get('DB_NAME'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    with conn.cursor() as cursor:
        sql = "SELECT temp, hum, created_at FROM temperature ORDER BY id DESC LIMIT 1"
        cursor.execute(sql)
        result = cursor.fetchone()

        if result:
            temp = result['temp']
            hum = result['hum']
            created_at = result['created_at']
            return {"temp": temp, "hum": hum, "created_at": created_at}
        else:
            return {"temp": None, "hum": None, "created_at": None}


def get_weather():
    """
    お天気情報取得
    """

    city_code = os.environ.get('CITY_CODE')
    base_url = "https://weather.tsukumijima.net/api/forecast"
    url = f"{base_url}?city={city_code}"
    response = requests.get(url)
    data = response.json()

    # ic(data)

    if response.status_code == 200:
        return data
    else:
        return {}

@app.route('/')
def index():
    dht_data = get_dht()
    weather_data = get_weather()
    return render_template('template.html', dht_data=dht_data, weather_data=weather_data, date=datetime.datetime.now())


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
