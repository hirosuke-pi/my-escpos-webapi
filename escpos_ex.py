
from escpos.printer import Usb
from escpos import *

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import unicodedata
import datetime


def get_east_asian_width_count(text):
    count = 0
    for c in text:
        if unicodedata.east_asian_width(c) in 'FWA':
            count += 2
        else:
            count += 1
    return count


def print_text(text, headers='', pil_obj=None):
    width = 390
    dt_now = datetime.datetime.now()
    im_resized = None
    if pil_obj is not None:
        ratio = 390 / pil_obj.width
        height_p = int(pil_obj.height * ratio) #(5)
        if height_p >= 1000:
            raise Exception('画像変換後の画像が縦1000pxを超えています')
        
        im_resized_tmp = pil_obj.resize((390, height_p), Image.LANCZOS)

        x1, y1, x2, y2 = 0, 0, 390, pil_obj.height+1
        im_resized = Image.new('RGB', (x2 - x1, y2 - y1), (255, 255, 255))
        im_resized.paste(im_resized_tmp, (-x1, -y1))
        im_resized.save('img/'+dt_now.strftime('%Y-%m-%d_%H-%M-%S')+'_IMG.png', quality=95)



    # テキスト配列化
    text_p =  headers + text
    sp_str = []
    col = 0
    col_str = ''
    for d in list(text_p):
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


    #画像化処理
    height =  len(sp_str) * 30

    if height < 1:
        raise Exception('印刷する文字がありません')
    elif height > 3000:
        raise Exception('100行を超えるテキストの印刷はできません')

    image_tmp = Image.new('1', (width, height), 255)
    draw = ImageDraw.Draw(image_tmp)
    font = ImageFont.truetype('RictyDiminished-Regular.ttf', 28, encoding='unic')
    
    #print(sp_str)
    counter_h = 0
    for l in sp_str:
        draw.text((0, counter_h), l, font=font, fill=0)
        counter_h += 30
    
    # 画像バグ防止
    x1, y1, x2, y2 = 0, 0, 390, height+1
    image = Image.new('RGB', (x2 - x1, y2 - y1), (255, 255, 255))
    image.paste(image_tmp, (-x1, -y1))
    image.save('img/'+dt_now.strftime('%Y-%m-%d_%H-%M-%S')+'.jpg', quality=95)


    # 印刷実行
    p = Usb(0x0416, 0x5011, 0, 0x81, 0x01)
    p.text(" ")
    p.image(image)
    if pil_obj is not None:
        p.image(im_resized)
    p.text(" ")
    p.cut()
    p.close()
    print("dsfgsgdsf")


def print_image(pil_obj):
    width = 390
    ratio = width / pil_obj.width
    height = int(pil_obj.height * ratio) #(5)
    im_resized = pil_obj.resize((width, height), Image.LANCZOS)

    # 印刷実行
    p = Usb(0x0416, 0x5011, 0, 0x81, 0x01)
    p.text(" ")
    p.image(im_resized)
    p.cut()
    p.close()