from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
import base64
import json

from websockets import sync
from websockets.sync import client
import requests

class FlyCrypto(object):
    def __init__(self):
        self.iv = bytes.fromhex("0"*32)

    def encrypt(self, text: str, key: str) -> dict:
        try:
            cipher = AES.new(key.encode(), AES.MODE_CBC, self.iv)
            data_pad = pad(text.encode(), AES.block_size)
            return {"enc": base64.b64encode(cipher.encrypt(data_pad)).decode(), "error": False}
        except Exception as er:
            return {"enc": str(er), "error": True}

    def decrypt(self, encoded_text: str, key: str) -> dict:
        try:
            decipher = AES.new(key.encode(), AES.MODE_CBC, self.iv)
            decoded_data = base64.b64decode(encoded_text)
            data_unpad = unpad(decipher.decrypt(decoded_data), AES.block_size)
            return {"dec": data_unpad.decode(), "error": False}
        except Exception as er:
            return {"dec": str(er), "error": True}

auth = "961cdb42e0e4409fa0846678a551a542"
websocket_url = "ws://127.0.0.1:3000/"
http_url = "http://127.0.0.1:3000/"

# متودایی که نیاز به رمزنگاری ندارن
# getHashtagsFromText, getTrends, getExploreTwitts, signup, signin

# ساخت اکانت
# data = requests.post(http_url+"signup", json={"fullname": "Ali", "username": "ali", "phone_number": "+989904541580"}).json()

# تایید اکانت
# data = requests.post(http_url+"signup", json={"fullname": "Ali", "username": "alireza", "phone_number": "+989904541580", "code": "2755"}).json()

# لاگین اکانت
# data = requests.post(http_url+"signin", json={"phone_number": "+989904541580"}).json()

# تایید لاگین اکانت
# data = requests.post(http_url+"signin", json={"phone_number": "+989904541580", "code": "2669"}).json()

# گرفتن هشتگا از یک متن
# data = requests.post(http_url+"getHashtagsFromText", json={"text": "Hi im #ali_reza and i work in #school, the #school elementry"}).json()
# output: {'ali_reza': 1, 'school': 2}

# گرفتن ترند ها
# with client.connect(websocket_url+"getTrends") as ws:
#     ws.send(json.dumps({"auth_token": "961cdb42e0e4409fa0846678a551a542"}))
#     print(ws.recv()) # Output: ['', '', '']

# ساختن توییت
# dt = FlyCrypto().encrypt(json.dumps({"auth_token": auth, "text": "امروز به #آدم خونگیام غذا دادم", "type": "text", "media": {}}), auth)
# data = requests.post(http_url+"addTwitt", json={"enc_data": dt['enc'], "powkey": auth}).json()
# data = FlyCrypto().decrypt(data['enc_data'], data['powkey'])
# print(data['dec'])

"""
{'status': 'OK', 'user': {'auth_token': '961cdb42e0e4409fa0846678a551a542', 'bio': '', 'followers': [], 'followings': [], 'fullname': 'Ali', 'has_tick': False, 'phone_number': '09904541580', 'profile_photo': '', 'settings': {'hide_phone_number': True, 'others_can_repost_my_twitts': True, 'show_my_followers': True, 'show_my_followings': True}, 'twts': [], 'user_id': 257184793350355, 'username': 'alireza'}}
"""