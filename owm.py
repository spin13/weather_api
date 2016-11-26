# -*- encoding: utf-8 -*-
import env
import requests
import json
import datetime
import slack
from pytz import timezone
from dateutil import parser

OWM_API_KEY = env.OWM_API_KEY

def get_forecast(lat='35.681298', lon='139.766247', cnt=3):
    ENDPOINT = 'http://api.openweathermap.org/data/2.5/forecast'
    params = {
        'APPID': OWM_API_KEY,
        # 'q': city,
        'lat': lat,
        'lon': lon,
        'units': 'metric',
        'cnt': cnt
    }
    res = requests.get(ENDPOINT, params=params)
    return res.json()

def get_weather(lat='35.681298', lon='139.766247'):
    ENDPOINT = 'http://api.openweathermap.org/data/2.5/forecast/daily'
    params = {
        'APPID': OWM_API_KEY,
        # 'q': city,
        'lat': lat,
        'lon': lon,
        'units': 'metric',
        'cnt': 1
    }
    res = requests.get(ENDPOINT, params=params)
    return res.json()

def get_sun(city='Tokyo'):
    ENDPOINT = 'http://api.openweathermap.org/data/2.5/weather'
    params = {
        'APPID': OWM_API_KEY,
        'q': city,
        'units': 'metric'
    }
    res = requests.get(ENDPOINT, params=params).json()
    ret = {
        'sunrise': unix_to_time(res['sys']['sunrise']).strftime("%H:%M"),
        'sunset': unix_to_time(res['sys']['sunset']).strftime("%H:%M")
    }
    return ret

# forecast3時間毎のデータ
def to_slack_list_forecast(data):
    ret = []
    for i in data:
        tmp={}
        tmp.update({'dt_txt': timezone('UTC').localize(parser.parse(i['dt_txt'])).astimezone(timezone('Asia/Tokyo')).strftime("%H:%M")})
        # tmp.update({'weather': i['weather'][0]['main']})
        # tmp.update({'description': i['weather'][0]['description']})
        tmp.update({'icon': i['weather'][0]['icon']})
        tmp.update({'temp': i['main']['temp']})
        ret.append(tmp)
    return ret

def to_slack_list_forecast_daily(data):
    tmp={}
    tmp.update({'icon': data['weather'][0]['icon']})
    tmp.update({'temp_min': data['temp']['min']})
    tmp.update({'temp_max': data['temp']['max']})
    return tmp

def to_slack_txt_daily(sun, daily):
    txt = ''
    txt += '>*' + datetime.datetime.now().strftime("%m月%d日") + 'の天気は*:' + str(daily['icon']) + ":\n"
    txt += '>気温：' + str(daily['temp_max']) + "℃/" + str(daily['temp_min']) + "℃\n"
    txt += '>日の出入：' + sun['sunrise'] + "/" + sun['sunset'] + "\n"
    return txt

def to_slack_txt_forecast(data):
    txt = ''
    for i in data:
        txt += '>*' + str(i['dt_txt']) + "*  "
        txt += ':' + str(i['icon']) + ":  "
        txt += '' + str(i['temp']) + "℃\n"
    return txt

def unix_to_time(t):
    return datetime.datetime.fromtimestamp(t)

if __name__ == '__main__':
    lat = '63.464138'
    lon = '142.773727'
    res_forecast = get_forecast(cnt=7)['list']
    res_weather = get_weather()['list'][0]
    sun = get_sun()
    forecast = to_slack_list_forecast(res_forecast)
    weather = to_slack_list_forecast_daily(res_weather)

    day_txt = to_slack_txt_daily(sun, weather)
    forecast_txt = to_slack_txt_forecast(forecast)
    slack.post_slack(
        username = 'weather_bot',
        channel = '#notice_weather',
        message = day_txt
    )
    slack.post_slack(
        username = 'weather_bot',
        channel = '#notice_weather',
        message = forecast_txt
    )

