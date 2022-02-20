#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys
import os
from dateutil import tz
import logging
import epd2in13_V3
import time
from datetime import datetime
from PIL import Image,ImageDraw,ImageFont
import traceback
from influxdb import InfluxDBClient
import locale

def drawText(im, x, y, f, txt, border=False, display=True):
    w, h = f.getsize(txt)
    if display:
        im.rectangle((x, y, x+w-1, y+h-1), fill = 255, outline=0 if border else 255)
        im.text((x, y), txt, font = f, fill = 0)
    return w, h

client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('teleinfo')

logging.basicConfig(level=logging.INFO)
exit_code=0
try:
    epd = epd2in13_V3.EPD()
    epd.init()
    epd.Clear(0xFF)

    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

    # Drawing on the image
    font18 = ImageFont.truetype('/usr/local/share/Font.ttc', 18)
    font24 = ImageFont.truetype('/usr/local/share/Font.ttc', 24)
    font48 = ImageFont.truetype('/usr/local/share/Font.ttc', 48)
    font72 = ImageFont.truetype('/usr/local/share/Font.ttc', 72)

    time_image = Image.new('1', (epd.height, epd.width), 255)
    time_draw = ImageDraw.Draw(time_image)

    epd.displayPartBaseImage(epd.getbuffer(time_image))
    num = 0
    while (True):
        res = client.query('SELECT value FROM PAPP, HCHC, HCHP WHERE time >= now()-1m LIMIT 1')
        #logging.info(res)
        try:
                dt = res.raw['series'][2]['values'][0][0]
                papp = res.raw['series'][2]['values'][0][1]
                hchc = res.raw['series'][0]['values'][0][1]
                hchp = res.raw['series'][1]['values'][0][1]
        except:
                papp = 0
                hchc = 0
                hchp = 0

        dt = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%SZ')
        dt = dt.replace(tzinfo=tz.tzutc())
        dt = dt.astimezone(tz.tzlocal())

        x, y = 0, 70
        w, h = drawText(time_draw, x, y, font18, f'PAPP ')
        w1, h1 = drawText(time_draw, x, y, font72, f'{papp}', display=False)
        drawText(time_draw, x+w, y+h-h1, font72, f' {papp}')

        x, y = 0, 0
        w, h = drawText(time_draw, x, y, font24, f'HC {round(hchc/1000, 1)}', display=False)
        w, h = drawText(time_draw, x, epd.width-h-4, font24, f'HC {round(hchc/1000, 1)}')
        w, _ = drawText(time_draw, x, y, font24, f'HP {round(hchp/1000,1)}', display=False)
        drawText(time_draw, epd.height-w-1, epd.width-h-4, font24, f'HP {round(hchp/1000,1)}')

        x, y = 0, 0
        drawText(time_draw, x, y, font18, datetime.strftime(dt, '%a %d/%m/%Y'))

        x, y = 0, 0
        w, h = drawText(time_draw, x, y, font18, datetime.strftime(dt, '%H:%M:%S'), display=False)
        drawText(time_draw, epd.height-w, y, font18, datetime.strftime(dt, '%H:%M:%S'))

        time_draw.line([(0, 20), (epd.height-1, 20)], fill = 0, width = 1)
        time_draw.line([(0, 95), (epd.height-1, 95)], fill = 0, width = 1)

        x, y = 25, 50
        time_draw.ellipse((x-8, y-8, x+8, y+8), fill = (num % 2) * 255)

        epd.displayPartial(epd.getbuffer(time_image))

        if False:
            time_image.save('/tmp/linky.png')
            break

        num = num + 1
        time.sleep(2)
        if num == 3600:
            epd.init()
            epd.Clear(0xFF)
            num = 0

except IOError as e:
    exit_code = 1
    logging.error(e)

except KeyboardInterrupt:
    pass


epd.init()
epd.Clear(0xFF)

epd.sleep()

sys.exit(exit_code)
