# Login - Signup by Number
# Add endpoint to return default_profile_encoded_bytes
# Add Profile Refresher

from .flyZone import FlyZone
from .flyCrypto import ( FlyCrypto, base64 )
from collections import Counter
from PIL import Image
from pymediainfo import MediaInfo
from mutagen import File
from typing import Literal
import httpx
import aiofiles
import schedule
import time
import random
import json
import threading
import re
import io
import os
import asyncio
import sqlite3

message_types = Literal['text', 'photo', 'video', 'music', 'file']

if not os.path.exists("hash_tags.json"):
    with open("hash_tags.json", "a") as f:
        f.write("{}")
        f.close()

async def extractHashTags(text: str):
    hashtags = re.findall(r'#\w+', text)
    hashtag_counts = Counter(tag[1:] for tag in hashtags)
    result = dict(hashtag_counts)
    return result

async def addToHashtags(hash_tags: dict):
    async with aiofiles.open("hash_tags.json", "r") as file:
        content: dict = json.loads( await file.read() )
        tags: list = list(content.keys())
        
        for tag in list(hash_tags.keys()):
            if tag in tags:
                content[tag] += hash_tags[tag]
            else: content[tag] = hash_tags[tag]
        
        await file.write( json.dumps(content, ensure_ascii=False ) )

async def sortHashTags():
    async with aiofiles.open("hash_tags.json", "r") as file:
        data = json.loads( await file.read() )
        top_10_max = sorted([d['value'] for d in data], reverse=True)[:10]
        return top_10_max

class Fly(object):
    def __init__(self):
        self.users = sqlite3.connect("users.db", check_same_thread=False)
        self.fly_zone = FlyZone()
        self.fly_crypto = FlyCrypto()
        self.http = httpx.AsyncClient()
        self.token = "2c9a19f7b75dd24ba7008f994d4cc7fd"
        self.pattern = r'^[qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890]*$'
        self.default_profile_encoded_bytes = "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"
        self.setup()

    def setup(self):
        self.users.execute(
            """
            CREATE TABLE IF NOT EXISTS users ( user_id INTEGER PRIMARY KEY, user_data TEXT )
            """
        )

    async def sendCode(self, phone: str):
        phone = await self.trim(phone)
        resp = await self.http.get(
            f"http://api-free.ir/api2/very/?token={self.token}&phone={phone}"
        )
        resp = resp.json()
        if resp['ok'] == True:
            return { "status": "OK", "sent": True, "message": resp['message'] }
        else: return { "status": "ERROR", "sent": False, "message": resp['message'] }

    async def acceptCode(self, phone: str, code: str):
        phone = await self.trim(phone)
        resp = await self.http.get(
            f"http://api-free.ir/api2/very/?token={self.token}&phone={phone}&code={code}"
        )
        resp = resp.json()
        if resp['ok'] == True:
            return { "status": "OK", "sent": True, "message": resp['message'] }
        else: return { "status": "ERROR", "sent": False, "message": resp['message'] }

    async def canDecode(self, text: str) -> bool:
        try:
            base64.b64decode(text.encode())
            return True
        except: return False

    async def getUsers(self) -> list:
        return self.users.execute("SELECT * FROM users").fetchall()
    
    async def getUserByID(self, user_id: int) -> dict:
        for user in await self.getUsers():
            if user[0] == user_id:
                return { "status": "OK", "user": json.loads(user[-1]) }
            
        return { "status": "INVALID_USER_ID" }
    
    async def getUserByAuth(self, auth_token: str) -> dict:
        for user in await self.getUsers():
            _user = json.loads(user[-1])
            if _user['auth_token'] == auth_token:
                return { "status": "OK", "user": _user }
            
        return { "status": "INVALID_AUTH_TOKEN" }
    
    async def getUserByUsername(self, username: str) -> dict:
        for user in await self.getUsers():
            _user = json.loads(user[-1])
            if _user['username'] == username:
                return { "status": "OK", "user": _user }
            
        return { "status": "INVALID_AUTH_TOKEN" }
    
    async def getUserByPhoneNumber(self, phone: str) -> dict:
        phone = await self.trim(phone)

        for user in await self.getUsers():
            _user = json.loads(user[-1])
            if _user['phone_number'] == phone:
                return { "status": "OK", "user": _user }
            
        return { "status": "INVALID_AUTH_TOKEN" }
    
    async def isExistsUsername(self, username: str) -> bool:
        for user in await self.getUsers():
            _user = json.loads(user[-1])
            if _user['username'] == username:
                return True
            
        return False
    
    async def isExistsPhoneNumber(self, phone_number: str) -> bool:
        phone_number = self.trimSync(phone_number)
        for user in await self.getUsers():
            _user = json.loads(user[-1])
            if _user['phone_number'] == phone_number:
                return True
            
        return False
    
    async def trim(self, phone_number: str):
        num = str(phone_number).strip()

        if num.startswith("0"): num = num[1:]
        elif num.startswith("98"): num = num[2:]
        elif num.startswith("+98"): num = num[3:]
        else: num = num

        return "0" + num
    
    def trimSync(self, phone_number: str):
        num = str(phone_number).strip()

        if num.startswith("0"): num = num[1:]
        elif num.startswith("98"): num = num[2:]
        elif num.startswith("+98"): num = num[3:]
        else: num = num

        return "0" + num
    
    def isProStringSync(self, string: str):
        return bool(re.match(self.pattern, string))
    
    async def add(
        self,
        fullname: str,
        username: str,
        phone_number: str,
        bio: str = ""
    ) -> dict:

        fullname = fullname.strip()
        username = username.strip().lower().replace(" ", "")
        bio = bio.strip()
        phone_number = await self.trim(phone_number)

        if username == "" or len(username) < 5:
            return { "status": "INVALID_ID" }
        
        is_pro_string = self.isProStringSync(username)
        
        if not is_pro_string:
            return { "status": "INVALID_ID" }

        if username.isdigit():
            return { "status": "INVALID_ID" }
        
        if not 0 <= len(bio) < 64:
            return { "status": "INVALID_BIO_LENGTH" }
        
        if not 1 < len(fullname) < 32:
            return { "status": "INVALID_FULLNAME_LENGTH" }
        
        stat = await self.isExistsUsername(username)
        ph_stat = await self.isExistsPhoneNumber(phone_number)
        
        if stat:
            return { "status": "EXISTS_USERNAME" }
        
        if ph_stat:
            return { "status": "EXISTS_PHONE_NUMBER" }
        
        user_auth = await self.fly_crypto.createAuth()
        user_id = await self.fly_crypto.createUserId()

        user = {
            "fullname": fullname,
            "username": username,
            "bio": bio,
            "phone_number": phone_number,
            "auth_token": user_auth,
            "user_id": user_id,
            "followers": [],
            "followings": [],
            "has_tick": False,
            "settings": {
                "hide_phone_number": True,
                "others_can_repost_my_twitts": True,
                "show_my_followings": True,
                "show_my_followers": True
            },
            "profile_photo": self.default_profile_encoded_bytes,
            "twts": []
        }

        self.users.execute("INSERT INTO users (user_id, user_data) VALUES (?, ?)", (user_id, json.dumps(user, ensure_ascii=False)))
        self.users.commit()

        return { "status": "OK", "user": user }
    
    async def update(
        self,
        auth_token: str,
        fullname: str = "",
        username: str = "",
        bio: str = "",
        profile_photo: str = "",
        hide_phone_number: bool = None,
        others_can_repost_my_twitts: bool = None,
        show_my_followings: bool = None,
        show_my_followers: bool = None
    ) -> dict:
        
        user = await self.getUserByAuth(auth_token)

        if user['status'] == "OK":
            fullname = fullname.strip()
            username = username.strip().lower().replace(" ", "")
            bio = bio.strip()
            profile_photo = profile_photo.strip()

            if username == "" or len(username) < 5:
                return { "status": "INVALID_ID" }
            
            is_pro_string = self.isProStringSync(username)
            can_decode = await self.canDecode(profile_photo)
            
            if not is_pro_string:
                return { "status": "INVALID_ID" }
            
            if not can_decode:
                return { "status": "INVALID_ENC" }

            if username.isdigit():
                return { "status": "INVALID_ID" }
            
            if not 0 <= len(bio) < 64:
                return { "status": "INVALID_BIO_LENGTH" }
            
            if not 1 < len(fullname) < 32:
                return { "status": "INVALID_FULLNAME_LENGTH" }
    
            new_user = {
                "fullname": fullname if not fullname == "" else user['user']['fullname'],
                "username": username if not username == "" else user['user']['username'],
                "bio": bio if not bio == "" else user['user']['bio'],
                "phone_number": user['user']['phone_number'],
                "auth_token": user['user']['auth_token'],
                "user_id": user['user']['user_id'],
                "followers": user['user']['followers'],
                "followings": user['user']['followings'],
                "has_tick": user['user']['has_tick'],
                "settings": {
                    "hide_phone_number": hide_phone_number if not hide_phone_number is None else user['user']['settings']['hide_phone_number'],
                    "others_can_repost_my_twitts": others_can_repost_my_twitts if not others_can_repost_my_twitts is None else user['user']['settings']['others_can_repost_my_twitts'],
                    "show_my_followings": show_my_followings if not show_my_followings is None else user['user']['show_my_followings'],
                    "show_my_followers": show_my_followers if not show_my_followers is None else user['user']['show_my_followers']
                },
                "profile_photo": profile_photo if not profile_photo == "" else user['user']['profile_photo'],
                "twts": user['user']['twts']
            }

            self.users.execute("UPDATE users SET user_data = ? WHERE user_id = ?", (json.dumps(new_user, ensure_ascii=False), user['user']['user_id']))
            self.users.commit()

            return { "status": "OK", "user": new_user }
        
        else: return user

    async def delete(
        self,
        auth_token: str
    ) -> dict:
        
        user = await self.getUserByAuth(auth_token)

        if user['status'] == "OK":
            self.users.execute("DELETE FROM users WHERE user_id = ?", (user['user']['user_id']))
            self.users.commit()
            return { "status": "OK" }
        else: return user

    async def addTick(self, user_auth: str):
        user = await self.getUserByAuth(user_auth)

        if user['status'] == "OK":

            user['user']['has_tick'] = True
            self.users.execute("UPDATE users SET user_data = ? WHERE user_id = ?", (json.dumps(user['user'], ensure_ascii=False), user['user']['user_id']))
            self.users.commit()

            return { "status": "OK", "user": user['user'] }

        else: return user

    async def removeTick(self, user_auth: str):
        user = await self.getUserByAuth(user_auth)

        if user['status'] == "OK":

            user['user']['has_tick'] = False
            self.users.execute("UPDATE users SET user_data = ? WHERE user_id = ?", (json.dumps(user['user'], ensure_ascii=False), user['user']['user_id']))
            self.users.commit()

            return { "status": "OK", "user": user['user'] }

        else: return user

    async def addTickByUsername(self, username: str):
        user = await self.getUserByUsername(username)

        if user['status'] == "OK":

            user['user']['has_tick'] = True
            self.users.execute("UPDATE users SET user_data = ? WHERE user_id = ?", (json.dumps(user['user'], ensure_ascii=False), user['user']['user_id']))
            self.users.commit()

            return { "status": "OK", "user": user['user'] }

        else: return user

    async def removeTickByUsername(self, username: str):
        user = await self.getUserByUsername(username)

        if user['status'] == "OK":

            user['user']['has_tick'] = False
            self.users.execute("UPDATE users SET user_data = ? WHERE user_id = ?", (json.dumps(user['user'], ensure_ascii=False), user['user']['user_id']))
            self.users.commit()

            return { "status": "OK", "user": user['user'] }

        else: return user

    async def follow(
        self,
        auth_token: str,
        following_user_id: int
    ) -> dict:
        
        user = await self.getUserByAuth(auth_token)
        follow = await self.getUserByID(following_user_id)

        if user['status'] == "OK":
            if follow['status'] == "OK":
                
                if not follow['user']['user_id'] in user['user']['user_id']:
                    user['user']['followings'].append(follow['user']['user_id'])
                
                return { "status": "OK" }
            
            else: return follow
        else: return user

    async def unfollow(
        self,
        auth_token: str,
        following_user_id: int
    ) -> dict:
        
        user = await self.getUserByAuth(auth_token)
        follow = await self.getUserByID(following_user_id)

        if user['status'] == "OK":
            if follow['status'] == "OK":
                
                if follow['user']['user_id'] in user['user']['user_id']:
                    user['user']['followings'].remove(follow['user']['user_id'])
                
                return { "status": "OK" }
            
            else: return follow
        else: return user


class FlyObject(object):
    def __init__(self):
        self.fly = Fly()

    async def photoAssert(self, photo: dict = {}) -> dict:
        keys: list = list(photo.keys())

        if len(keys) == 0: return { "status": "INVALID_KEYS_LENGTH" }
        if not "enc_bytes" in keys: return { "status": "UNCOVERD_ENC_BYTES" }

        return { "status": "OK" }
    
    async def videoAssert(self, video: dict = {}) -> dict:
        keys: list = list(video.keys())

        if len(keys) == 0: return { "status": "INVALID_KEYS_LENGTH" }
        if not "enc_bytes" in keys: return { "status": "UNCOVERD_ENC_BYTES" }

        return { "status": "OK" }
    
    async def musicAssert(self, music: dict = {}) -> dict:
        keys: list = list(music.keys())

        if len(keys) == 0: return { "status": "INVALID_KEYS_LENGTH" }
        if not "enc_bytes" in keys: return { "status": "UNCOVERD_ENC_BYTES" }

        return { "status": "OK" }
    
    async def fileAssert(self, file: dict = {}) -> dict:
        keys: list = list(file.keys())

        if len(keys) == 0: return { "status": "INVALID_KEYS_LENGTH" }
        if not "enc_bytes" in keys: return { "status": "UNCOVERD_ENC_BYTES" }

        return { "status": "OK" }
    
    async def findByID(self, user_id: int, twitted_id: int) -> dict:
        user = await self.fly.getUserByID(user_id)

        if user['status'] == "OK":
            indx = 0
            for twitts in user['user']['twts']:
                if twitts['twitted_id'] == twitted_id:
                    return { "status": "OK", "twitted": twitts, "twitt_index": indx }
                
                indx += 1
            
            return { "status": "INVALID_TWITTED_ID" }
        else: return user

    async def findReplyByID(self, user_id: int, twitted_id: int, twitted_reply_id: int):
        user = await self.fly.getUserByID(user_id)

        if user['status'] == "OK":
            for twitts in user['user']['twts']:
                if twitts['twitted_id'] == twitted_id:
                    indx = 0
                    for replies in twitts['replies']:
                        if replies['twitted_id'] == twitted_reply_id:
                            return { "status": "OK", "twitted": replies, "twitt_reply_index": indx }

                        indx += 1
                    
                    return { "status": "INVALID_TWITTED_REPLY_ID" }
            return { "status": "INVALID_TWITTED_ID" }
        else: return user
    
    async def addTwitt(
        self,
        auth_token: str,
        text: str,
        type: message_types = "text",
        media: dict = {}
    ) -> dict:
        
        user = await self.fly.getUserByAuth(auth_token)

        if user['status'] == "OK":
            text = text.strip()

            if not 1 <= len(text) <= 125:
                return { "status": "INVALID_TEXT_LENGTH" }
            
            if type == "text":
                message = {
                    "fullname": user['user']['fullname'],
                    "username": user['user']['username'],
                    "has_tick": user['user']['has_tick'],
                    "user_id": user['user']['user_id'],
                    "message_type": "text",
                    "text_length": len(text),
                    "twitted_id": await self.fly.fly_crypto.createTwittId(),
                    "text": text,
                    "likes": 0,
                    "who_liked": [],
                    "reposts": 0,
                    "profile_photo": user['user']['profile_photo'],
                    "media": {},
                    "replies": []
                }
            
            elif type == "photo":
                photo = await self.photoAssert(media)
                if photo['status'] == "OK":
                    can_decode = await self.fly.canDecode(media['enc_data'])
                    if can_decode:
                        try:
                            decrypted = base64.b64decode(media['enc_data'].encode())
                            image_stream = io.BytesIO(decrypted)
                            with Image.open(image_stream) as img:
                                width, height = img.size
                            
                            message = {
                                "fullname": user['user']['fullname'],
                                "username": user['user']['username'],
                                "has_tick": user['user']['has_tick'],
                                "user_id": user['user']['user_id'],
                                "message_type": "photo",
                                "text_length": len(text),
                                "twitted_id": await self.fly.fly_crypto.createTwittId(),
                                "text": text,
                                "likes": 0,
                                "who_liked": [],
                                "reposts": 0,
                                "profile_photo": user['user']['profile_photo'],
                                "media": {
                                    "width": width,
                                    "height": height,
                                    "size": len(decrypted),
                                    "enc_data": media['enc_data']
                                },
                                "replies": []
                            }

                        except Exception as errorProcess: return { "status": "ERROR_ADDING", "message": errorProcess }
                    else: return { "status": "INVALID_ENC" }
                else: return { "status": "INVALID_MEIDA_INPUT" }
            
            elif type == "file":
                file = await self.fileAssert(media)
                if file['status'] == "OK":
                    can_decode = await self.fly.canDecode(media['enc_data'])
                    if can_decode:
                        try:
                            decrypted = base64.b64decode(media['enc_data'].encode())
                            dec = len(decrypted)
                            
                            message = {
                                "fullname": user['user']['fullname'],
                                "username": user['user']['username'],
                                "has_tick": user['user']['has_tick'],
                                "user_id": user['user']['user_id'],
                                "message_type": "file",
                                "text_length": len(text),
                                "twitted_id": await self.fly.fly_crypto.createTwittId(),
                                "text": text,
                                "likes": 0,
                                "who_liked": [],
                                "reposts": 0,
                                "profile_photo": user['user']['profile_photo'],
                                "media": {
                                    "size": dec,
                                    "enc_data": media['enc_data']
                                },
                                "replies": []
                            }

                        except Exception as errorProcess: return { "status": "ERROR_ADDING", "message": errorProcess }
                    else: return { "status": "INVALID_ENC" }
                else: return { "status": "INVALID_MEIDA_INPUT" }

            elif type == "music":
                music = await self.musicAssert(media)
                if music['status'] == "OK":
                    can_decode = await self.fly.canDecode(media['enc_data'])
                    if can_decode:
                        try:
                            decrypted = base64.b64decode(media['enc_data'].encode())
                            music_stream = io.BytesIO(decrypted)
                            music = File(music_stream)
                            duration = music.info.length
                            
                            message = {
                                "fullname": user['user']['fullname'],
                                "username": user['user']['username'],
                                "has_tick": user['user']['has_tick'],
                                "user_id": user['user']['user_id'],
                                "message_type": "music",
                                "text_length": len(text),
                                "twitted_id": await self.fly.fly_crypto.createTwittId(),
                                "text": text,
                                "likes": 0,
                                "who_liked": [],
                                "reposts": 0,
                                "profile_photo": user['user']['profile_photo'],
                                "media": {
                                    "size": len(decrypted),
                                    "duration": duration,
                                    "enc_data": media['enc_data']
                                },
                                "replies": []
                            }

                        except Exception as errorProcess: return { "status": "ERROR_ADDING", "message": errorProcess }
                    else: return { "status": "INVALID_ENC" }
                else: return { "status": "INVALID_MEIDA_INPUT" }

            elif type == "video":
                video = await self.videoAssert(media)
                if video['status'] == "OK":
                    can_decode = await self.fly.canDecode(media['enc_data'])
                    if can_decode:
                        try:
                            decrypted = base64.b64decode(media['enc_data'].encode())
                            video_stream = io.BytesIO(decrypted)
                            clip = MediaInfo.parse(video_stream)
                            video_track = next((track for track in clip.tracks if track.track_type == "Video"), None)
                            if video_track == None: return { "status": "NOT_VIDEO_BYTES" }
                            height, width, duration = video_track.height, video_track.width, video_track.duration // 1000
                            
                            message = {
                                "fullname": user['user']['fullname'],
                                "username": user['user']['username'],
                                "has_tick": user['user']['has_tick'],
                                "user_id": user['user']['user_id'],
                                "message_type": "video",
                                "text_length": len(text),
                                "twitted_id": await self.fly.fly_crypto.createTwittId(),
                                "text": text,
                                "likes": 0,
                                "who_liked": [],
                                "reposts": 0,
                                "profile_photo": user['user']['profile_photo'],
                                "media": {
                                    "size": len(decrypted),
                                    "duration": duration,
                                    "height": height,
                                    "width": width,
                                    "enc_data": media['enc_data']
                                },
                                "replies": []
                            }

                        except Exception as errorProcess: return { "status": "ERROR_ADDING", "message": errorProcess }
                    else: return { "status": "INVALID_ENC" }
                else: return { "status": "INVALID_MEIDA_INPUT" }

            user['user']['twts'].append(message)
            tags = await extractHashTags(message['text'])
            await addToHashtags(tags)
            self.fly.users.execute("UPDATE users SET user_data = ? WHERE user_id = ?", (json.dumps(user['user'], ensure_ascii=False), user['user']['user_id']))
            self.fly.users.commit()
            
            return { "status": "OK", "twitted": message }
        
        else: return user

    async def removeTwitt(
        self,
        auth_token: str,
        twitted_id: int
    ) -> int:
        
        user = await self.fly.getUserByAuth(auth_token)
        msg = await self.findByID(user['user']['user_id'], twitted_id)

        if user['status'] == "OK":
            if msg['status'] == "OK":
                tw = { "twitted_index": 0, "deleted": True }
                for twitts in user['user']['twts']:
                    if twitts['twitted_id'] == twitted_id:
                        user['user']['twts'].pop(tw['twitted_index'])
                        tw['deleted'] = True
                    
                    tw['twitted_index'] += 1

                self.fly.users.execute("UPDATE users SET user_data = ? WHERE user_id = ?", (json.dumps(user['user'], ensure_ascii=False), user['user']['user_id']))
                self.fly.users.commit()
                
                return { "status": "OK", "removed": tw['deleted'], "twitt_id": twitted_id }

                # user['user']['twts'].remove(msg['twitted'])
                # return { "status": "OK", "removed_twitt": msg['twitted'] }
            else: return msg
        else: return user
        
    async def addTwittReply(
        self,
        auth_token: str,
        to: int,
        twitted_id: int,
        text: str,
        type: message_types = "text",
        media: dict = {}
    ) -> dict:
        
        user = await self.fly.getUserByAuth(auth_token)
        to_user = await self.fly.getUserByID(to)
        twitt = await self.findByID(to, twitted_id)

        if user['status'] == "OK":
            if to_user['status'] == "OK":
                if twitt['status'] == "OK":
                    text = text.strip()

                    if not 1 <= len(text) <= 125:
                        return { "status": "INVALID_TEXT_LENGTH" }
                    
                    if type == "text":
                        message = {
                            "fullname": user['user']['fullname'],
                            "username": user['user']['username'],
                            "has_tick": user['user']['has_tick'],
                            "user_id": user['user']['user_id'],
                            "message_type": "text",
                            "text_length": len(text),
                            "twitted_id": await self.fly.fly_crypto.createTwittId(),
                            "text": text,
                            "likes": 0,
                            "who_liked": [],
                            "profile_photo": user['user']['profile_photo'],
                            "media": {}
                        }
                    
                    elif type == "photo":
                        photo = await self.photoAssert(media)
                        if photo['status'] == "OK":
                            can_decode = await self.fly.canDecode(media['enc_data'])
                            if can_decode:
                                try:
                                    decrypted = base64.b64decode(media['enc_data'].encode())
                                    image_stream = io.BytesIO(decrypted)
                                    with Image.open(image_stream) as img:
                                        width, height = img.size
                                    
                                    message = {
                                        "fullname": user['user']['fullname'],
                                        "username": user['user']['username'],
                                        "has_tick": user['user']['has_tick'],
                                        "user_id": user['user']['user_id'],
                                        "message_type": "photo",
                                        "text_length": len(text),
                                        "twitted_id": await self.fly.fly_crypto.createTwittId(),
                                        "text": text,
                                        "likes": 0,
                                        "who_liked": [],
                                        "profile_photo": user['user']['profile_photo'],
                                        "media": {
                                            "width": width,
                                            "height": height,
                                            "size": len(decrypted),
                                            "enc_data": media['enc_data']
                                        }
                                    }

                                except Exception as errorProcess: return { "status": "ERROR_ADDING", "message": errorProcess }
                            else: return { "status": "INVALID_ENC" }
                        else: return { "status": "INVALID_MEIDA_INPUT" }
                    
                    elif type == "file":
                        file = await self.fileAssert(media)
                        if file['status'] == "OK":
                            can_decode = await self.fly.canDecode(media['enc_data'])
                            if can_decode:
                                try:
                                    decrypted = base64.b64decode(media['enc_data'].encode())
                                    dec = len(decrypted)
                                    
                                    message = {
                                        "fullname": user['user']['fullname'],
                                        "username": user['user']['username'],
                                        "has_tick": user['user']['has_tick'],
                                        "user_id": user['user']['user_id'],
                                        "message_type": "file",
                                        "text_length": len(text),
                                        "twitted_id": await self.fly.fly_crypto.createTwittId(),
                                        "text": text,
                                        "likes": 0,
                                        "who_liked": [],
                                        "profile_photo": user['user']['profile_photo'],
                                        "media": {
                                            "size": dec,
                                            "enc_data": media['enc_data']
                                        }
                                    }

                                except Exception as errorProcess: return { "status": "ERROR_ADDING", "message": errorProcess }
                            else: return { "status": "INVALID_ENC" }
                        else: return { "status": "INVALID_MEIDA_INPUT" }

                    elif type == "music":
                        music = await self.musicAssert(media)
                        if music['status'] == "OK":
                            can_decode = await self.fly.canDecode(media['enc_data'])
                            if can_decode:
                                try:
                                    decrypted = base64.b64decode(media['enc_data'].encode())
                                    music_stream = io.BytesIO(decrypted)
                                    music = File(music_stream)
                                    duration = music.info.length
                                    
                                    message = {
                                        "fullname": user['user']['fullname'],
                                        "username": user['user']['username'],
                                        "has_tick": user['user']['has_tick'],
                                        "user_id": user['user']['user_id'],
                                        "message_type": "music",
                                        "text_length": len(text),
                                        "twitted_id": await self.fly.fly_crypto.createTwittId(),
                                        "text": text,
                                        "likes": 0,
                                        "who_liked": [],
                                        "profile_photo": user['user']['profile_photo'],
                                        "media": {
                                            "size": len(decrypted),
                                            "duration": duration,
                                            "enc_data": media['enc_data']
                                        }
                                    }

                                except Exception as errorProcess: return { "status": "ERROR_ADDING", "message": errorProcess }
                            else: return { "status": "INVALID_ENC" }
                        else: return { "status": "INVALID_MEIDA_INPUT" }

                    elif type == "video":
                        video = await self.videoAssert(media)
                        if video['status'] == "OK":
                            can_decode = await self.fly.canDecode(media['enc_data'])
                            if can_decode:
                                try:
                                    decrypted = base64.b64decode(media['enc_data'].encode())
                                    video_stream = io.BytesIO(decrypted)
                                    clip = MediaInfo.parse(video_stream)
                                    video_track = next((track for track in clip.tracks if track.track_type == "Video"), None)
                                    if video_track == None: return { "status": "NOT_VIDEO_BYTES" }
                                    height, width, duration = video_track.height, video_track.width, video_track.duration // 1000
                                    
                                    message = {
                                        "fullname": user['user']['fullname'],
                                        "username": user['user']['username'],
                                        "has_tick": user['user']['has_tick'],
                                        "user_id": user['user']['user_id'],
                                        "message_type": "video",
                                        "text_length": len(text),
                                        "twitted_id": await self.fly.fly_crypto.createTwittId(),
                                        "text": text,
                                        "likes": 0,
                                        "who_liked": [],
                                        "profile_photo": user['user']['profile_photo'],
                                        "media": {
                                            "size": len(decrypted),
                                            "duration": duration,
                                            "height": height,
                                            "width": width,
                                            "enc_data": media['enc_data']
                                        }
                                    }

                                except Exception as errorProcess: return { "status": "ERROR_ADDING", "message": errorProcess }
                            else: return { "status": "INVALID_ENC" }
                        else: return { "status": "INVALID_MEIDA_INPUT" }

                    twitt['twitted']['replies'].append(message)
                    del to_user['user']['twts'][twitt['twitt_index']]
                    to_user['user']['twts'].insert(twitt['twitt_index'], twitt['twitted'])
                    tags = await extractHashTags(message['text'])
                    await addToHashtags(tags)
                    self.fly.users.execute("UPDATE users SET user_data = ? WHERE user_id = ?", (json.dumps(to_user['user'], ensure_ascii=False), to_user['user']['user_id']))
                    self.fly.users.commit()
                    
                    return { "status": "OK", "twitted": message }
                
        else: return user

    async def refreshTwitts(self):
        for user in await self.fly.getUsers():
            _user = json.loads(user[-1])

            for twitts in _user['twts']:
                msg_owner = await self.fly.getUserByID(twitts['user_id'])

                twitts['fullname'] = msg_owner['user']['fullname']
                twitts['username'] = msg_owner['user']['username']
                twitts['has_tick'] = msg_owner['user']['has_tick']
                twitts['profile_photo'] = msg_owner['user']['profile_photo']

                for reply in twitts['replies']:
                    msg_owner = await self.fly.getUserByID(reply['user_id'])

                    reply['fullname'] = msg_owner['user']['fullname']
                    reply['username'] = msg_owner['user']['username']
                    reply['has_tick'] = msg_owner['user']['has_tick']
                    reply['profile_photo'] = msg_owner['user']['profile_photo']
            
            self.fly.users.execute("UPDATE users SET user_data = ? WHERE user_id = ?", (json.dumps(_user, ensure_ascii=False), _user['user_id']))
            self.fly.users.commit()

            print(f"Updated {_user['user_id']}")

    async def likeTwitt(
        self,
        auth_token: str,
        to: int,
        twitted_id: int
    ) -> dict:
        
        user = await self.fly.getUserByAuth(auth_token)
        to_user = await self.fly.getUserByID(to)

        if user['status'] == "OK":
            if to_user['status'] == "OK":
                twitted = await self.findByID(to, twitted_id)

                if twitted['status'] == "OK":

                    if not user['user']['user_id'] in twitted['twitted']['who_liked']:
                        twitted['twitted']['who_liked'].append(user['user']['user_id'])
                        twitted['twitted']['likes'] += 1
                    
                        to_user['user']['twts'].pop(twitted['twitt_index'])
                        to_user['user']['twts'].insert(twitted['twitt_index'], twitted['twitted'])

                        self.fly.users.execute("UPDATE users SET user_data = ? WHERE user_id = ?", (json.dumps(to_user['user'], ensure_ascii=False), to))
                        self.fly.users.commit()

                    return { "status": "OK", "twitt": twitted['twitted'] }
                else: return twitted
            else: return to_user
        else: return user

    async def unlikeTwitt(
        self,
        auth_token: str,
        to: int,
        twitted_id: int
    ) -> dict:
        
        user = await self.fly.getUserByAuth(auth_token)
        to_user = await self.fly.getUserByID(to)

        if user['status'] == "OK":
            if to_user['status'] == "OK":
                twitted = await self.findByID(to, twitted_id)

                if twitted['status'] == "OK":

                    if user['user']['user_id'] in twitted['twitted']['who_liked']:
                        twitted['twitted']['who_liked'].remove(user['user']['user_id'])
                        twitted['twitted']['likes'] -= 1
                    
                        to_user['user']['twts'].pop(twitted['twitt_index'])
                        to_user['user']['twts'].insert(twitted['twitt_index'], twitted['twitted'])

                        self.fly.users.execute("UPDATE users SET user_data = ? WHERE user_id = ?", (json.dumps(to_user['user'], ensure_ascii=False), to))
                        self.fly.users.commit()

                    return { "status": "OK", "twitt": twitted['twitted'] }
                else: return twitted
            else: return to_user
        else: return user

    async def likeTwittReply(
        self,
        auth_token: str,
        to: int,
        twitted_id: int,
        twitted_reply_id: int
    ) -> dict:
        
        user = await self.fly.getUserByAuth(auth_token)
        to_user = await self.fly.getUserByID(to)

        if user['status'] == "OK":
            if to_user['status'] == "OK":
                twitted = await self.findByID(to, twitted_id)

                if twitted['status'] == "OK":
                    reply_twitted = await self.findReplyByID(to, twitted_id, twitted_reply_id)

                    if reply_twitted['status'] == "OK":
                        if not user['user']['user_id'] in reply_twitted['twitted']['who_liked']:
                            reply_twitted['twitted']['who_liked'].append(user['user']['user_id'])
                            reply_twitted['twitted']['likes'] += 1

                            twitted['twitted']['replies'].pop(reply_twitted['twitt_reply_index'])
                            twitted['twitted']['replies'].insert(reply_twitted['twitt_reply_index'], reply_twitted['twitted'])


                            to_user['user']['twts'].pop(twitted['twitt_index'])
                            to_user['user']['twts'].insert(twitted['twitt_index'], twitted['twitted'])

                            self.fly.users.execute("UPDATE users SET user_data = ? WHERE user_id = ?", (json.dumps(to_user['user'], ensure_ascii=False), to))
                            self.fly.users.commit()

                        return { "status": "OK", "twitt": twitted['twitted'] }
                    else: return reply_twitted
                else: return twitted
            else: return to_user
        else: return user

    async def unlikeTwittReply(
        self,
        auth_token: str,
        to: int,
        twitted_id: int,
        twitted_reply_id: int
    ) -> dict:
        
        user = await self.fly.getUserByAuth(auth_token)
        to_user = await self.fly.getUserByID(to)

        if user['status'] == "OK":
            if to_user['status'] == "OK":
                twitted = await self.findByID(to, twitted_id)

                if twitted['status'] == "OK":
                    reply_twitted = await self.findReplyByID(to, twitted_id, twitted_reply_id)

                    if reply_twitted['status'] == "OK":
                        if user['user']['user_id'] in reply_twitted['twitted']['who_liked']:
                            reply_twitted['twitted']['who_liked'].remove(user['user']['user_id'])
                            reply_twitted['twitted']['likes'] -= 1

                            twitted['twitted']['replies'].pop(reply_twitted['twitt_reply_index'])
                            twitted['twitted']['replies'].insert(reply_twitted['twitt_reply_index'], reply_twitted['twitted'])


                            to_user['user']['twts'].pop(twitted['twitt_index'])
                            to_user['user']['twts'].insert(twitted['twitt_index'], twitted['twitted'])

                            self.fly.users.execute("UPDATE users SET user_data = ? WHERE user_id = ?", (json.dumps(to_user['user'], ensure_ascii=False), to))
                            self.fly.users.commit()

                        return { "status": "OK", "twitt": twitted['twitted'] }
                    else: return reply_twitted
                else: return twitted
            else: return to_user
        else: return user

    async def repostTwitt(
        self,
        auth_token: str,
        from_user_id: int,
        twitted_id: int
    ) -> dict:
        
        user = await self.fly.getUserByAuth(auth_token)
        from_user = await self.fly.getUserByID(from_user_id)
        
        if user['status'] == "OK":
            if from_user['status'] == "OK":
                if from_user['user']['settings']['others_can_repost_my_twitts']:

                    twitted = await self.findByID(from_user_id, twitted_id)

                    if twitted['status'] == "OK":

                        twitted['twitted']['reposts'] += 1
                        from_user['user']['twts'].pop(twitted['twitt_index'])
                        from_user['user']['twts'].insert(twitted['twitt_index'], twitted['twitted'])

                        self.fly.users.execute("UPDATE users SET user_data = ? WHERE user_id = ?", (json.dumps(from_user['user'], ensure_ascii=False), from_user_id))
                        self.fly.users.commit()

                        return await self.addTwitt(
                            auth_token,
                            twitted['twitted']['text'],
                            twitted['twitted']['message_type'],
                            twitted['twitted']['media']
                        )

                    else: return twitted
                else: return { "status": "UNABLE_REPOST" }
            else: return from_user
        else: return user

    async def getRandomTwitts(self):
        users = await self.fly.getUsers()
        twitts = set()
        selected_users = [u for u in users]

        for _ in range(20):
            if len(selected_users) > 0:
                rnd_user = random.choice(selected_users)
                _user = json.loads(rnd_user[-1])
                if len(_user['twts']) > 0:
                    twitts.add(
                        random.choice(_user['twts'])
                    )
            else: pass
        
        return { "status": "OK", "twitts": list(twitts) }

    async def getTrendTags(self):
        return await sortHashTags()

# ----------------------

from rich import print

fly_object = FlyObject()

def run_asyncio_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()

def twitts_schedule_task():
    schedule.every(10).seconds.do(lambda: asyncio.run(fly_object.refreshTwitts()))

def run_pending():
    threading.Thread(target=run_asyncio_loop, daemon=True).start()
    twitts_schedule_task()
    
    while True:
        schedule.run_pending()
        time.sleep(10)
        print("-"*32)
