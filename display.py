import logging
import os
import sys
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from sensors import get_hue_temp
from weather import get_weather
from weather_icons import get_weather_icon

sys.path.append('lib')
font_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'font')
images_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')

from waveshare_epd import epd7in5_V2

weather_data = get_weather()
logging.debug(weather_data)

epd = epd7in5_V2.EPD()


def fill_template():
    with Image.open(os.path.join(images_dir, 'template.png')) as template:
        global draw
        draw = ImageDraw.Draw(template)
        draw_main_weather()
        draw_today_info()
        draw_next_days()
        draw_update_time()
        draw_sub_temps()
        output = os.path.join(images_dir, 'output.png')
        template.save(output)
        return output


def draw_text(x, y, text, font_size=50, fill='rgb(0,0,0)'):
    draw.text((x, y), text,
              font=ImageFont.truetype(os.path.join(font_dir, 'Roboto-Regular.ttf'), font_size),
              fill=fill)


def draw_symbol(x, y, text, font_size=50, fill='rgb(0,0,0)'):
    draw.text((x, y), text,
              font=ImageFont.truetype(os.path.join(font_dir, 'weathericons-regular-webfont.ttf'), font_size),
              fill=fill)


def draw_main_weather():
    y_pos = 5
    font_size = 180
    draw_symbol(5, y_pos-20, weather_data['icon_code'], font_size)
    draw_text(260, y_pos, weather_data['temp_current'], font_size)


def draw_today_info():
    font_size = 50
    line_y = 200
    icon_x = 15
    text_x = 65

    if datetime.now() > weather_data['sunset'] or datetime.now() < weather_data['sunrise']:
        timeofday = 'night'
    else:
        timeofday = 'day'
    lines = [
        ('thermometer', f"{weather_data['temp_min']}-{weather_data['temp_max']}"),
        ('wind', f"{weather_data['wind']}"),
        ('barometer', f"{weather_data['pressure']}"),
        ('humidity', f"{weather_data['humidity']}", 'rain', f"{weather_data['rain_percent']}")
    ]

    for i, line in enumerate(lines):
        line_offset = i*font_size
        draw_symbol(icon_x, line_y+line_offset, get_weather_icon(line[0], timeofday))
        draw_text(text_x, line_y+line_offset+5, line[1])
        if len(line) > 2:
            draw_symbol(icon_x+160, line_y+line_offset, get_weather_icon(line[2]))
            draw_text(text_x+165, line_y+line_offset, line[3])


def draw_next_days():
    font_size = 40
    x_pos = 375
    y_pos = 290
    for i in range(1, 4):
        x_padding = 140*(i-1)
        day_weather = weather_data[f'day_{i}']
        draw_text(x_pos+x_padding, y_pos, day_weather['date'], font_size)
        draw_symbol(x_pos+x_padding+30, y_pos+font_size-5, day_weather['icon_code'], font_size)
        draw_text(x_pos+x_padding, y_pos+(font_size*2), f"{day_weather['temp_min']}-{day_weather['temp_max']}", font_size)
        draw_symbol(x_pos+x_padding, y_pos+(font_size*3), get_weather_icon('rain'), font_size)
        draw_text(x_pos+x_padding+45, y_pos+(font_size*3)+10, day_weather['rain_percent'], font_size)


def draw_update_time():
    current_time = datetime.now().strftime('%H:%M')
    draw_text(45, 430, f"Updated: {current_time}", font_size=40, fill="rgb(255,255,255)")


def draw_sub_temps():
    x_pos = 410
    y_pos = 180
    font_size = 50
    draw_text(x_pos, y_pos, f"Feels like: {weather_data['feels_like']}")
    draw_text(x_pos, y_pos+font_size, f"Inside: {get_hue_temp()}")


def write_to_screen(image_file):
    logging.info("Setting up image")
    image_to_apply = Image.new('1', (epd.width, epd.height), 255)
    screen_output_file = Image.open(image_file)
    image_to_apply.paste(screen_output_file, (0, 0))
    logging.info("Initing Display")
    epd.init()
    if datetime.now().minute == 0 and datetime.now().hour == 2:
        logging.info("Refreshing display")
        epd.Clear()
    logging.info("Applied image")
    epd.display(epd.getbuffer(image_to_apply))


if __name__ == '__main__':
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(funcName)s() - %(message)s')
    output = fill_template()
    write_to_screen(output)
