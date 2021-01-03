import sys, os
import traceback
import datetime
import base64
import io
from PIL import Image

from flask import Flask, make_response, request
from flask_cors import CORS, cross_origin
import json

import escpos_ex
 

api = Flask(__name__)
CORS(api)

cmd_list = ['print']
res_json = {
    'status' : 'success',
    'msg-jp' : ''
}


@api.route('/print', methods=["GET", "POST", "OPTIONS"])
@cross_origin()
def get_user():
    global cmd_list
    escpos_ex.set_patlite_progress(1)

    if request.method == "GET":
        return send_req_error('許可されていないメソッドです', 405)

    req_json = request.json
    #print(req_json)

    # 必須情報確認
    if req_json == None or 'user' not in req_json or 'text' not in req_json or 'state' not in req_json:
        return send_req_error('必須項目user, text, stateがありません', 406)

    text = req_json['text'].strip()
    user = req_json['user'].strip().replace('\n', '')
    state = req_json['state'].strip().replace('\n', '')

    if len(user) < 1 or len(state) < 1:
        return send_req_error('ステート又はユーザー名が空欄です', 406)

    # ヘッダ生成
    dt_now = datetime.datetime.now()
    headers =  'DATE: '+ dt_now.strftime('%Y/%m/%d %H:%M:%S') +'\n'
    headers += 'IP  : '+ request.remote_addr +'\n'
    headers += 'STAT: '+ state +'\n' 
    headers += 'USER: '+ user +'\n'
    headers += '-'*27

    # 画像ある場合
    pil_obj = None
    if 'img' in req_json:
        image_dec = None
        try:
            image_dec = base64.b64decode(req_json['img'])
            pil_obj = Image.open(io.BytesIO(image_dec))
        except:
            print(traceback.format_exc())
            type_, value_, traceback_ = sys.exc_info()
            return send_req_error('画像データをデコードできませんでした - ' + str(value_), 406)
    
    escpos_ex.set_patlite_progress(2)
    try:
        escpos_ex.print_text(text, headers, pil_obj)
    except Exception as e:
        print(traceback.format_exc())
        type_, value_, traceback_ = sys.exc_info()
        return send_req_error('印刷エラー - '+ str(value_), 506)
    
    escpos_ex.set_patlite_progress(4)
    return send_req_success('印刷完了しました')
    


@api.errorhandler(404)
def not_found(error):
    return send_req_error('無効なページです', 404)


def send_req_error(msg, code):
    global res_json
    res_json['status'] = 'error'
    res_json['msg-jp'] = msg
    escpos_ex.set_patlite_progress(0)
    escpos_ex.set_patlite('200000', '5')
    return make_response(json.dumps(res_json, ensure_ascii=False), code)

def send_req_success(msg):
    global res_json
    res_json['status'] = 'success'
    res_json['msg-jp'] = msg
    return make_response(json.dumps(res_json, ensure_ascii=False), 201)
    
 
 
if __name__ == '__main__':
    api.run(host='0.0.0.0', port=8880)