import logging
import os
from datetime import datetime

import requests

from weather_icons import get_weather_icon

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass


def get_weather():
    api_key = os.environ['api_key']
    latitude = os.environ['latitude']
    longitude = os.environ['longitude']
    units = os.environ.get('units', 'metric')
    speed_unit = {'metric': 'KMH', 'imperial': 'MPH'}
    temp_unit = {'metric': '\N{DEGREE SIGN}C', 'imperial': '\N{DEGREE SIGN}F'}

    url = f'http://api.openweathermap.org/data/2.5/onecall?lat={latitude}&lon={longitude}&units={units}&appid={api_key}'

    def generate_next_day(day_data):
        next_day_dict = {
            'date': datetime.fromtimestamp(day_data['dt']).strftime("%d/%m"),
            'icon_code': get_weather_icon(day_data['weather'][0]['id']),
            'temp_max': f"{day_data['temp']['max']:.0f}",
            'temp_min': f"{day_data['temp']['min']:.0f}",
            'rain_percent': f"{day_data['pop'] * 100:.0f}%",
        }
        return next_day_dict

    error_connect = True
    while error_connect:
        try:
            logging.info('[Weather] Connecting')
            response = requests.get(url)
            logging.info('[Weather] Connected')
            error_connect = None
        except requests.exceptions.RequestException:
            logging.error('[Weather] Connection Error')

    error = None
    while not error:
        if response.status_code == 200:
            logging.info('[Weather] 200')
            data = response.json()

            current = data['current']
            weather = current['weather']
            daily_weather = data['daily'][0]
            daily_temp = daily_weather['temp']

            w_dict = {
                'description': weather[0]['description'].title(),
                'feels_like': f"{current['feels_like']:.0f}{temp_unit[units]}",
                'humidity': f"{current['humidity']}%",
                'icon_code': get_weather_icon(weather[0]['id']),
                'pressure': f"{current['pressure']} PA",
                'rain_percent': f"{ daily_weather['pop']*100:.0f}%",
                'sunrise': datetime.fromtimestamp(current['sunrise']),
                'sunset': datetime.fromtimestamp(current['sunset']),
                'temp_current': f"{current['temp']:.1f}{temp_unit[units]}",
                'temp_max': f"{daily_temp['max']:.0f}{temp_unit[units]}",
                'temp_min': f"{daily_temp['min']:.0f}",
                'temp_unit': temp_unit[units],
                'wind_direction': f"{current['wind_deg']}",
                'wind': f"{current['wind_speed']} {speed_unit[units]}",
            }
            for i in range(1, 4):
                w_dict[f'day_{i}'] = generate_next_day(data['daily'][i])

            return w_dict
        else:
            logging.error(f"[Weather] Can't connect to {url}")


if __name__ == '__main__':
    from pprint import pprint
    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(funcName)s() - %(message)s')
    pprint(get_weather())
