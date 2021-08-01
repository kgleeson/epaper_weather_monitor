import logging
import os

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass


def get_hue_temp():
    hue_url = os.environ['hue_url']
    logging.info('Attempting to connect to Hue.')
    response = requests.get(hue_url)
    logging.info('Connection to Hue successful.')
    if response.status_code == 200:
        # get data in jason format
        parsed_hue_data = response.json()
        return f"{parsed_hue_data['state']['temperature'] / 100.0}\N{DEGREE SIGN}C"


if __name__ == '__main__':
    from pprint import pprint
    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(funcName)s() - %(message)s')
    pprint(get_hue_temp())
