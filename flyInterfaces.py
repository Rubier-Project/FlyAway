from typing import Literal
from json import dumps

message_types = Literal['text', 'photo', 'video', 'music', 'file', 'nonetype']

class UserSettings(object):
    def __init__(self, abstracted: dict = {}):
        
        self.__result__ = abstracted

        self.hide_phone_number: bool = self.__result__.get("hide_phone_number", True)
        self.others_can_repost_my_twitts: bool = self.__result__.get("others_can_repost_my_twitts", True)
        self.show_my_followings: bool = self.__result__.get("show_my_followings", True)
        self.show_my_followers: bool = self.__result__.get("show_my_followers", True)

    def __str__(self):
        return dumps( self.__result__, ensure_ascii=False, indent=2 )
    
    def __repr__(self):
        return dumps( self.__result__, ensure_ascii=False, indent=2 )

class Media(object):
    def __init__(self, abstracted: dict = {}):
        
        self.__result__ = abstracted
        self.enc_bytes: str = self.__result__.get("enc_bytes", "")
        self.__isarray__ = self.isArray()
        self.size: int = self.__result__.get("size", 0)
        self.width: int = self.__result__.get("width", 0)
        self.height: int = self.__result__.get("height", 0)
        self.duration: int = self.__result__.get("duration", 0)
        if self.enc_bytes != "":
            if isinstance(self.__isarray__, bytes):
                self.real_bytes: bytes = self.__isarray__
            else: self.real_bytes: bytes = b''
        else: self.real_bytes: bytes = b''

    def isArray(self):
        import base64
        try:
            return base64.b64decode(self.enc_bytes.encode())
        except:return False

    def __str__(self):
        return dumps( self.__result__, ensure_ascii=False, indent=2 )
    
    def __repr__(self):
        return dumps( self.__result__, ensure_ascii=False, indent=2 )

class TwittReply(object):
    def __init__(self, abstracted: dict = {}):
        
        self.__result__ = abstracted

        self.fullname: str = self.__result__.get("fullname", "null")
        self.username: str = self.__result__.get("username", "null")
        self.has_tick: bool = self.__result__.get("has_tick", False)
        self.user_id: str = self.__result__.get("user_id", "null")
        self.message_type: message_types = self.__result__.get("message_type", "nonetype")
        self.text_length: int = self.__result__.get("text_length", 0)
        self.text: str = self.__result__.get("text", "")
        self.likes: str = self.__result__.get("likes", 0)
        self.who_liked: list[str] = self.__result__.get("who_liked", [])
        self.profile_photo: str = self.__result__.get("profile_photo", "null")
        self.media: Media = Media(self.__result__.get("media", {}))

    def __str__(self):
        return dumps( self.__result__, ensure_ascii=False, indent=2 )
    
    def __repr__(self):
        return dumps( self.__result__, ensure_ascii=False, indent=2 )

class Twitt(object):
    def __init__(self, abstracted: dict = {}):
        
        self.__result__ = abstracted

        self.fullname: str = self.__result__.get("fullname", "null")
        self.username: str = self.__result__.get("username", "null")
        self.has_tick: bool = self.__result__.get("has_tick", False)
        self.user_id: str = self.__result__.get("user_id", "null")
        self.message_type: message_types = self.__result__.get("message_type", "nonetype")
        self.text_length: int = self.__result__.get("text_length", 0)
        self.text: str = self.__result__.get("text", "")
        self.likes: str = self.__result__.get("likes", 0)
        self.who_liked: list[str] = self.__result__.get("who_liked", [])
        self.reposts: int = self.__result__.get("reposts", 0)
        self.profile_photo: str = self.__result__.get("profile_photo", "null")
        self.media: Media = Media(self.__result__.get("media", {}))
        self.replies: list[TwittReply] = [TwittReply(twitt) for twitt in self.__result__.get("replies", [])]

    def __str__(self):
        return dumps( self.__result__, ensure_ascii=False, indent=2 )
    
    def __repr__(self):
        return dumps( self.__result__, ensure_ascii=False, indent=2 )

class User(object):
    def __init__(self, abstracted: dict = {}):
        
        self.__result__ = abstracted

        self.fullname: str = self.__result__.get("fullname", "null")
        self.username: str = self.__result__.get("username", "null")
        self.bio: str = self.__result__.get("bio", "")
        self.phone_number: str = self.__result__.get("phone_number", "null")
        self.user_id: str = self.__result__.get("user_id", "null")
        self.auth_token: str = self.__result__.get("auth_token", "null")
        self.profile_photo: str = self.__result__.get("profile_photo", "null")
        self.settings: UserSettings = UserSettings(self.__result__.get("settings", {}))
        self.has_tick: bool = self.__result__.get("has_tick", False)
        if self.settings.show_my_followers:
            self.followers: list[User] = [User(user) for user in self.__result__.get("followers", [])]
        else: self.followers: list[User] = []
        if self.settings.show_my_followings:
            self.followings: list[User] = [User(user) for user in self.__result__.get("followings", [])]
        else: self.followings: list[User] = []
        self.twitts: list[Twitt] = [Twitt(twitted) for twitted in self.__result__.get("twts", [])]

    def __str__(self):
        return dumps( self.__result__, ensure_ascii=False, indent=2 )
    
    def __repr__(self):
        return dumps( self.__result__, ensure_ascii=False, indent=2 )