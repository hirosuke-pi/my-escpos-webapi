
from escpos.printer import Usb
from escpos import *

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import datetime

# レシートプリンターを使った印刷

"""
width = 500
height = 250

image = Image.new('1', (width, height), 255)
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('RictyDiminished-Regular.ttf', 28, encoding='unic')

draw.text((0, 82), "abcdefghijklmnopqrstuvwxyz1", font=font, fill=0) #27
draw.text((0, 112), "ABCDEFGHIJKLMNOPQRSTUVWXYZ1", font=font, fill=0)
draw.text((0, 142), "1234567890" + " ", font=font, fill=0)
draw.text((0, 172), "!\"#$%&'()=~|+*<>?_{}" + " ", font=font, fill=0)

p = Usb(0x0416, 0x5011, 0, 0x81, 0x01)
p.text("Hello World\n")
p.image(image)
p.cut()
"""


import unicodedata


def get_east_asian_width_count(text):
    count = 0
    for c in text:
        if unicodedata.east_asian_width(c) in 'FWA':
            count += 2
        else:
            count += 1
    return count


def printer_p(text, user):
    text = text.strip()
    user = user.strip()
    if not(1 < get_east_asian_width_count(text) <= 135 and 1 < get_east_asian_width_count(user) < 27):
        return "エラー"

    width = 390
    height = 180 + 30

    image = Image.new('1', (width, height), 255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('RictyDiminished-Regular.ttf', 28, encoding='unic')

    dt_now = datetime.datetime.now()

    text =  '['+ dt_now.strftime('%Y-%m-%d %H:%M:%S')+ ']\n'+user +':\n'+ text
    sp_str = []
    col = 0
    col_str = ''
    for d in list(text):
        if col >= 27 or d == '\n':
            sp_str.append(col_str)
            col = 0
            col_str = ''
            if d == '\n':
                continue

        col += get_east_asian_width_count(d)
        col_str += d

    if len(d) > 0:
        sp_str.append(col_str)
    
    print(sp_str)
    counter = 0
    for l in sp_str:
        draw.text((0, counter), l, font=font, fill=0)
        counter += 30
    
    if counter < height:
        image = image.crop((0, 0, width, counter))
    image.save('test.jpg', quality=95)

    p = Usb(0x0416, 0x5011, 0, 0x81, 0x01)
    p.text(" ")
    p.image(image)
    p.cut()

    return True


d = printer_p("s" * 135, "hirosuke-pi")
print(d)