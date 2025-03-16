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
WorkingDirectory=/home/pi/rasp_display
ExecStart=/usr/bin/python3 /home/pi/rasp_display/app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```
sudo systemctl enable app.service
sudo systemctl status app.service
```

# /home/display/start_kiosk.sh

```
#!/bin/sh
# 自動起動定義
# /home/display/.config/lxsession/LXDE-pi/autostart
chromium-browser --noerrdialogs --kiosk --incognito http://localhost:5000

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
