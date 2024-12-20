# from websockets.sync import client
# from websockets import connect
# from Cryptodome.Cipher import AES
# from Cryptodome.Util.Padding import pad, unpad
# from rich import print
# import base64
# import json
# import time
# import requests
# import asyncio

# class FlyCrypto(object):
#     def __init__(self):
#         self.iv = bytes.fromhex("0"*32)

#     def encrypt(self, text: str, key: str) -> dict:
#         try:
#             cipher = AES.new(key.encode(), AES.MODE_CBC, self.iv)
#             data_pad = pad(text.encode(), AES.block_size)
#             return {"enc": base64.b64encode(cipher.encrypt(data_pad)).decode(), "error": False}
#         except Exception as er:
#             return {"enc": str(er), "error": True}

#     def decrypt(self, encoded_text: str, key: str) -> dict:
#         try:
#             decipher = AES.new(key.encode(), AES.MODE_CBC, self.iv)
#             decoded_data = base64.b64decode(encoded_text)
#             data_unpad = unpad(decipher.decrypt(decoded_data), AES.block_size)
#             return {"dec": data_unpad.decode(), "error": False}
#         except Exception as er:
#             return {"dec": str(er), "error": True}

# url = "ws://127.0.0.1:3000/getUserByIdHandshake"
# fly = FlyCrypto()

# with client.connect(url) as ws:
#     enc_data = fly.encrypt(json.dumps({"auth_token": "407b9f3fa9d749a195145b40f6606f32", "user_id": 135663765438490}), "7cf3144d6c98454dbfd920677da89240")['enc']
#     ws.send(
#         json.dumps(
#             {
#                 "enc_data": enc_data,
#                 "powkey": "7cf3144d6c98454dbfd920677da89240"
#             }
#         )
#     )
#     msg = json.loads(ws.recv())
#     print(json.loads(fly.decrypt(msg['enc_data'], msg['powkey'])['dec']))

# async def a():
#     async with connect(url) as ws:
#         enc_data = fly.encrypt(json.dumps({"auth_token": "407b9f3fa9d749a195145b40f6606f32", "user_id": 135663765438490}), "7cf3144d6c98454dbfd920677da89240")['enc']
#         for _ in range(10):
#             await ws.send(
#                 json.dumps(
#                     {
#                         "enc_data": enc_data,
#                         "powkey": "7cf3144d6c98454dbfd920677da89240"
#                     }
#                 )
#             )
#             msg = json.loads(await ws.recv())
#             print(json.loads(fly.decrypt(msg['enc_data'], msg['powkey'])['dec']))

# asyncio.run(a())

# print(requests.post("http://127.0.0.1:3000/signup", json={"fullname": "Yasin", "username": "mhdyr", "phone_number": "+989904541580", "code": "9140"}).json())
"""
{'status': 'OK', 'user': {'auth_token': '407b9f3fa9d749a195145b40f6606f32', 'bio': '', 'followers': [], 'followings': [], 'fullname': 'Yasin', 'has_tick': False, 'pho
ne_number': '09904541580', 'profile_photo': '', 'settings': {'hide_phone_n
umber': True, 'others_can_repost_my_twitts': True, 'show_my_followers': True, 'show_my_followings': True}, 'twts': [], 'user_id': 135663765438490, 'username': 'mhdyr'
}}
"""