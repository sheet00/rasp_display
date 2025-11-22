from flask import Flask, render_template
import os
import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
import pymysql
from icecream import ic
from bs4 import BeautifulSoup
import logging
import json



load_dotenv()
app = Flask(__name__, static_folder='static')

# HTTPリクエスト設定
REQUEST_TIMEOUT = 10  # 秒

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# リトライ設定付きHTTPセッション作成
def create_retry_session():
    retry_strategy = Retry(
        total=3,  # 最大3回リトライ
        backoff_factor=2,  # 指数関数バックオフ (2^n秒)
        status_forcelist=[429, 500, 502, 503, 504],  # リトライするHTTPステータス
        allowed_methods=["HEAD", "GET", "OPTIONS"],  # リトライ対象メソッド
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.timeout = REQUEST_TIMEOUT  # デフォルトタイムアウト設定
    return session

# グローバルセッション
http_session = create_retry_session()


def get_dht():
    """
    部屋の温度取得
    """
    conn = None
    try:
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
    except Exception as e:
        return {"temp": None, "hum": None, "created_at": None}

def get_weather_livedoor():
    """
    お天気情報取得 livedoor
    """

    def custom_date_label(forecast):
        japanese_days = ["日","月", "火", "水", "木", "金", "土"]
        target_date = datetime.datetime.strptime(forecast['date'], '%Y-%m-%d')
        day_of_week = target_date.strftime('%w')
        date_label = f"{target_date.strftime('%d')}日({japanese_days[int(day_of_week)]})"
        return date_label

    ic("-"*100)
    ic("get_weather_livedoor")

    city_code = os.environ.get('CITY_CODE')
    base_url = "https://weather.tsukumijima.net/api/forecast"
    url = f"{base_url}?city={city_code}"
    response = http_session.get(url)
    data = response.json()

    ic(data['location'])
    # ic(data['forecasts'][0])
    if response.status_code == 200:
        # ラベル処理
        for forecast in data['forecasts']:
            forecast['custom_date_label'] = custom_date_label(forecast)

        return data
    else:
        return {}
    
def get_weather_open():
    """
    直近の予測気温取得 (OpenWeather)

    Returns:
        dict: {'dt_txt_jst': '2025-11-22 15:00:00', 'temp': 17.86} 形式
              エラー時は空の辞書 {}
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
    response = http_session.get(base_url, params=params)

    if response.status_code != 200:
        logger.error(f"天気API (OpenWeather) エラー - ステータス: {response.status_code}, レスポンス: {response.text[:500]}")
        return {}

    # JSON パース
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        logger.error(f"天気API (OpenWeather) JSON decode エラー: {e}")
        logger.error(f"レスポンステキスト: {response.text[:500]}")
        return {}

    # list[0]から直近の予測データを取得
    if 'list' not in data or len(data['list']) == 0:
        logger.error("天気API (OpenWeather) list データが空です")
        return {}

    latest_forecast = data['list'][0]

    # UTC → JST変換
    dt_utc = datetime.datetime.fromtimestamp(latest_forecast['dt'], tz=datetime.timezone.utc)
    dt_jst = dt_utc + datetime.timedelta(hours=9)

    # 必要なデータだけ返す
    recent_weather_forecast = {
        'dt_jst': dt_jst,
        'temp': latest_forecast['main']['temp']
    }

    ic(recent_weather_forecast)

    return recent_weather_forecast

def get_forecast_comment():
    """
    ウェザーニュース最新見解取得
    """

    url = os.environ.get('WEATHER_DESCRIPTION_URL')
    response = http_session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    forecast_comment = soup.find('div', class_='forecast-comment')
    if not forecast_comment:
        return "テキストが見つかりませんでした"
    
    description = forecast_comment.text
    return description

@app.route('/')
def index():
    try:
        dht_data = get_dht()
        weather_data = get_weather_livedoor()
        forecast_comment = get_forecast_comment()
        recent_weather = get_weather_open()

        return render_template('template.html',
                            dht_data=dht_data,
                            weather_data=weather_data,
                            forecast_comment=forecast_comment,
                            recent_weather=recent_weather,
                            date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        logger.error(f"リクエスト処理エラー: {str(e)}", exc_info=True)
        return f"エラーが発生しました: {str(e)}", 500


if __name__ == '__main__':
    logger.info("アプリケーション開始")
    app.run(debug=True, host='0.0.0.0', port=5000)
