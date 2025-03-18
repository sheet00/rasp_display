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


def get_weather_livedoor():
    """
    お天気情報取得 livedoor
    """
    ic("-"*100)
    ic("get_weather_livedoor")

    city_code = os.environ.get('CITY_CODE')
    base_url = "https://weather.tsukumijima.net/api/forecast"
    url = f"{base_url}?city={city_code}"
    response = requests.get(url)
    data = response.json()

    ic(data['location'])

    if response.status_code == 200:
        weather_open_data = get_weather_open()
        if weather_open_data and 'list' in weather_open_data and len(weather_open_data['list']) > 0:
            # openweatherの最初の予報の最高気温と最低気温を取得
            max_temp = weather_open_data['list'][0]['main']['temp_max']
            min_temp = weather_open_data['list'][0]['main']['temp_min']

            # livedoorの予報の最高気温と最低気温を更新
            if 'forecasts' in data and len(data['forecasts']) > 0:
                data['forecasts'][0]['temperature']['max']['celsius'] = str(max_temp) if max_temp is not None else None
                data['forecasts'][0]['temperature']['min']['celsius'] = str(min_temp) if min_temp is not None else None
        return data
    else:
        return {}
    
def get_weather_open():
    """
    お天気情報取得 openweather
    """
    ic("-"*100)
    ic("get_weather_open")

    city_id = os.environ.get('OPENWEATHER_CITY_ID')
    api_key = os.environ.get('OPENWEATHER_API_KEY')
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    
    params = {
        "id": city_id,
        "appid": api_key,
        "lang": "ja",
        "units": "metric"
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        # JSTに変換
        for item in data["list"]:
            dt_utc = datetime.datetime.fromtimestamp(item['dt'], tz=datetime.timezone.utc)
            dt_jst = dt_utc + datetime.timedelta(hours=9)
            item['dt_txt'] = dt_jst.strftime('%Y-%m-%d %H:%M:%S')

        ic(data["city"])
        # ic(data['list'][0])

        return data
    else:
        return {}

def get_forecast_comment():
    """
    ウェザーニュース最新見解取得
    """
    from bs4 import BeautifulSoup
    import requests
    import os

    url = os.environ.get('WEATHER_DESCRIPTION_URL')
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    forecast_comment = soup.find('div', class_='forecast-comment')
    if not forecast_comment:
        return "テキストが見つかりませんでした"
    
    description = forecast_comment.text
    return description

@app.route('/')
def index():
    dht_data = get_dht()
    weather_livedoor = get_weather_livedoor()
    forecast_comment = get_forecast_comment()

    return render_template('template.html',
                        dht_data=dht_data,
                        weather_data=weather_livedoor,
                        forecast_comment=forecast_comment,
                        date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
