from flask import Flask, render_template
import os
import pymysql
import requests
from icecream import ic

app = Flask(__name__)


def get_dht():
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
    api_key = os.environ.get('OPENWEATHER_API_KEY')
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    city = os.environ.get('CITY')
    
    url = f"{base_url}?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()

    ic(data)
    
    if response.status_code == 200:
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"{weather_description}, {temperature}°C"
    else:
        return "取得不可"

@app.route('/')
def index():
    dht_data = get_dht()
    weather_data = get_weather()
    return render_template('template.html', temperature=dht_data['temp'], humidity=dht_data['hum'], created_at=dht_data['created_at'], weather=weather_data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
