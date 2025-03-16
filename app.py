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

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return "Hello, World!"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
