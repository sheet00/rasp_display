# rasp_display

## 概要

このシステムは、Flask で記述された Web アプリケーションです。

部屋の温度と湿度をデータベースから取得し、Livedoor 天気 API および OpenWeather API から天気情報を取得して、それらの情報を `template.html` テンプレートに渡して表示します。

# systemctl メモ

```
[Unit]
Description=Python App Service
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/rasp_display/
ExecStart=/home/pi/.pyenv/versions/3.13.3/bin/python app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```
sudo systemctl enable python_app.service
sudo systemctl status python_app.service
sudo systemctl restart python_app.service
```

# 画面スリープオフ

```
sudo raspi-config
Display Options -> D4 Screen Blanking disable
```


# openweathermap

https://openweathermap.org/forecast5

# livedoor

https://weather.tsukumijima.net/

## 環境設定

このアプリケーションは、以下の環境変数を必要とします。

- `DB_HOST`: データベースのホスト名
- `DB_USER`: データベースのユーザー名
- `DB_PASSWORD`: データベースのパスワード
- `DB_NAME`: データベース名
- `CITY_CODE`: Livedoor 天気 API で使用する都市コード
- `OPENWEATHER_API_KEY`: OpenWeather API キー
- `OPENWEATHER_CITY_ID`: OpenWeather API で使用する都市 ID
