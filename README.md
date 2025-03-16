# rasp_display

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
