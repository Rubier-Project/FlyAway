from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
import uuid
import base64

class FlyCrypto(object):
    def __init__(self):
        self.secret = "BYTES-+UASYD*A&)(A&DUSAO&DUDAugfdighyfduigduyghydfughdfghyuiD&*)D*A^D&A(*^SD&*ASNDERCOVER_DSA_[DS],{}324465465464478632.432"
        self.iv = bytes.fromhex("0"*32)
    
    async def createAuth(self) -> str:
        return uuid.uuid4().hex
    
    async def createUserId(self) -> int:
        return uuid.uuid4().node
    
    async def createTwittId(self) -> int:
        return uuid.uuid4().node

    async def encrypt(self, text: str, key: str) -> dict:
        try:
            cipher = AES.new(key.encode(), AES.MODE_CBC, self.iv)
            data_pad = pad(text.encode(), AES.block_size)
            return {"enc": base64.b64encode(cipher.encrypt(data_pad)).decode(), "error": False}
        except Exception as er:
            return {"enc": str(er), "error": True}

    async def decrypt(self, encoded_text: str, key: str) -> dict:
        try:
            decipher = AES.new(key.encode(), AES.MODE_CBC, self.iv)
            decoded_data = base64.b64decode(encoded_text)
            data_unpad = unpad(decipher.decrypt(decoded_data), AES.block_size)
            return {"dec": data_unpad.decode(), "error": False}
        except Exception as er:
            return {"dec": str(er), "error": True}
