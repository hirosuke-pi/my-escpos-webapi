import requests

import base64


def image_file_to_base64(file_path):
    with open(file_path, "rb") as image_file:
        data = base64.b64encode(image_file.read())

    return data.decode('utf-8')


r = requests.post('http://192.168.1.100:8880/print', 
                  json={"user" : "hirosuke-pi", "state" : "DiscordBot", "text" : 
"""テスト""",
"img" : image_file_to_base64("C:\\Users\\test\\Desktop\\lena_square.png")
})

print(r.status_code)
print(r.json())
