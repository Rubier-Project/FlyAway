from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
import base64
import json

from websockets import sync
from websockets.sync import client
import requests

from rich import print_json as print

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

auth = "7cf3144d6c98454dbfd920677da89240"
websocket_url = "ws://127.0.0.1:3000/"
http_url = "http://127.0.0.1:3000/"

# متودایی که نیاز به رمزنگاری ندارن
# getHashtagsFromText, getTrends, getExploreTwitts, signup, signin

# ساخت اکانت
# data = requests.post(http_url+"signup", json={"fullname": "Ali", "username": "ali", "phone_number": "+989904541580"}).json()

# تایید اکانت
#data = requests.post(http_url+"signup", json={"fullname": "Ali", "username": "alireza", "phone_number": "+989904541580", "code": "5804"}).json()

# لاگین اکانت
#data = requests.post(http_url+"signin", json={"phone_number": "+989904541580"}).json()


# تایید لاگین اکانت
# data = requests.post(http_url+"signin", json={"phone_number": "+989904541580", "code": "4605"}).json()
# print(data)

# گرفتن هشتگا از یک متن
# data = requests.post(http_url+"getHashtagsFromText", json={"text": "Hi im #ali_reza and i work in #school, the #school elementry"}).json()
# output: {'ali_reza': 1, 'school': 2}
# print(data)

# گرفتن ترند ها
# with client.connect(websocket_url+"getTrends") as ws:
#     ws.send(json.dumps({"auth_token": "7cf3144d6c98454dbfd920677da89240"}))
#     print(ws.recv()) # Output: ['', '', '']

# ساختن توییت
# dt = FlyCrypto().encrypt(json.dumps({"auth_token": auth, "text": "امروز به #آدم خونگیام غذا دادم", "type": "text", "media": {}}), auth)
# data = requests.post(http_url+"addTwitt", json={"enc_data": dt['enc'], "powkey": auth}).json()
# data = FlyCrypto().decrypt(data['enc_data'], data['powkey'])
# print(data['dec'])

# حذف توییت
# dt = FlyCrypto().encrypt(json.dumps({"auth_token": auth, "twitted_id": 40518999166239}), auth)
# data = requests.post(http_url+"removeTwitt", json={"enc_data": dt['enc'], "powkey": auth}).json()
# data = FlyCrypto().decrypt(data['enc_data'], data['powkey'])
# print(data['dec'])

# ریپلای زدن به یک توییت
# dt = FlyCrypto().encrypt(json.dumps({"auth_token": auth, "to": 127594846192093, "twitted_id": 193441301453347,"text": "امروز به #آدم خونگیام غذا دادم", "type": "text", "media": {}}), auth)
# data = requests.post(http_url+"addTwittReply", json={"enc_data": dt['enc'], "powkey": auth}).json()
# data = FlyCrypto().decrypt(data['enc_data'], data['powkey'])
# print(data['dec'])

# لایک یک توییت
# dt = FlyCrypto().encrypt(json.dumps({"auth_token": auth, "to": 127594846192093, "twitted_id": 193441301453347}), auth)
# data = requests.post(http_url+"likeTwitt", json={"enc_data": dt['enc'], "powkey": auth}).json()
# data = FlyCrypto().decrypt(data['enc_data'], data['powkey'])
# print(data['dec'])

# آنلایک یک توییت
# dt = FlyCrypto().encrypt(json.dumps({"auth_token": auth, "to": 127594846192093, "twitted_id": 193441301453347}), auth)
# data = requests.post(http_url+"unlikeTwitt", json={"enc_data": dt['enc'], "powkey": auth}).json()
# data = FlyCrypto().decrypt(data['enc_data'], data['powkey'])
# print(data['dec'])

# لایک ریپلای یک توییت
# dt = FlyCrypto().encrypt(json.dumps({"auth_token": auth, "to": 127594846192093, "twitted_id": 193441301453347, "twitted_reply_id": 34408195522044}), auth)
# data = requests.post(http_url+"likeTwittReply", json={"enc_data": dt['enc'], "powkey": auth}).json()
# data = FlyCrypto().decrypt(data['enc_data'], data['powkey'])
# print(data['dec'])

# آنلایک ریپلای یک توییت
# dt = FlyCrypto().encrypt(json.dumps({"auth_token": auth, "to": 127594846192093, "twitted_id": 193441301453347, "twitted_reply_id": 34408195522044}), auth)
# data = requests.post(http_url+"unlikeTwittReply", json={"enc_data": dt['enc'], "powkey": auth}).json()
# data = FlyCrypto().decrypt(data['enc_data'], data['powkey'])
# print(data['dec'])

# گرفتن اطلاعات اوت با وب سوکت
# with client.connect(websocket_url+"getMeHandshake") as ws:
#     dt = FlyCrypto().encrypt(json.dumps({"auth_token": auth}), auth)
#     ws.send(json.dumps({"enc_data": dt['enc'], "powkey": auth}))
#     data = json.loads(ws.recv())
#     data = FlyCrypto().decrypt(data['enc_data'], data['powkey'])
#     print(data['dec'])

# گرفتن اطلاعات اوت
# dt = FlyCrypto().encrypt(json.dumps({"auth_token": auth}), auth)
# data = requests.post(http_url+"getMe", json={"enc_data": dt['enc'], "powkey": auth}).json()
# data = FlyCrypto().decrypt(data['enc_data'], data['powkey'])
# print(data['dec'])

# گرفتن توییت های یک کاربر
# with client.connect(websocket_url+"getUserTwitts") as ws:
#     dt = FlyCrypto().encrypt(json.dumps({"auth_token": auth, "user_id": 127594846192093}), auth)
#     ws.send(json.dumps({"enc_data": dt['enc'], "powkey": auth}))
#     data = json.loads(ws.recv())
#     data = FlyCrypto().decrypt(data['enc_data'], data['powkey'])
#     print(data['dec'])

# گرفتن اطلاعات کاربر با وب سوکت
# with client.connect(websocket_url+"getUserByIdHandshake") as ws:
#     dt = FlyCrypto().encrypt(json.dumps({"auth_token": auth, "user_id": 127594846192093}), auth)
#     ws.send(json.dumps({"enc_data": dt['enc'], "powkey": auth}))
#     data = json.loads(ws.recv())
#     data = FlyCrypto().decrypt(data['enc_data'], data['powkey'])
#     print(data['dec'])

# ریپوست کردن
# with client.connect(websocket_url+"repostTwitt") as ws:
#     dt = FlyCrypto().encrypt(json.dumps({"auth_token": auth, "from_user_id": 127594846192093, "twitted_id": 193441301453347}), auth)
#     ws.send(json.dumps({"enc_data": dt['enc'], "powkey": auth}))
#     data = json.loads(ws.recv())
#     data = FlyCrypto().decrypt(data['enc_data'], data['powkey'])
#     print(data['dec'])

# فالو کردن
# dt = FlyCrypto().encrypt(json.dumps({"auth_token": auth, "following_user_id": 127594846192093}), auth)
# data = requests.post(http_url+"follow", json={"enc_data": dt['enc'], "powkey": auth}).json()
# data = FlyCrypto().decrypt(data['enc_data'], data['powkey'])
# print(data['dec'])

# آنفالو کردن
# dt = FlyCrypto().encrypt(json.dumps({"auth_token": auth, "following_user_id": 127594846192093}), auth)
# data = requests.post(http_url+"unfollow", json={"enc_data": dt['enc'], "powkey": auth}).json()
# data = FlyCrypto().decrypt(data['enc_data'], data['powkey'])
# print(data['dec'])

# آپدیت پروفایل
# هرچی بهش بدیو ادیت میزنه فقط
# dt = FlyCrypto().encrypt(json.dumps({"auth_token": auth, "fullname": "Ali Reza Mmdy"}), auth)
# data = requests.post(http_url+"updateProfile", json={"enc_data": dt['enc'], "powkey": auth}).json()
# data = FlyCrypto().decrypt(data['enc_data'], data['powkey'])
# print(data['dec'])

# حذف اکانت
# dt = FlyCrypto().encrypt(json.dumps({"auth_token": auth}), auth)
# data = requests.post(http_url+"deleteAccount", json={"enc_data": dt['enc'], "powkey": auth}).json()
# data = FlyCrypto().decrypt(data['enc_data'], data['powkey'])
# print(data['dec'])


"""
{'status': 'OK', 'user': {'auth_token': '7cf3144d6c98454dbfd920677da89240', 'bio': '', 'followers': [], 'followings': [], 'fullname': 'Ali', 'has_tick': False, 'phone_number': '09904541580', 'profile_photo': '', 'settings': {'hide_phone_number': True, 'others_can_repost_my_twitts': True, 'show_my_followers': True, 'show_my_followings': True}, 'twts': [], 'user_id': 127594846192093, 'username': 'alireza'}}
"""