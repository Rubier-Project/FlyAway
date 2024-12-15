from pytz import timezone
from datetime import datetime

class FlyZone(object):
    def __init__(self):pass

    def getSync(self) -> datetime:
        return datetime.now(timezone("Asia/Tehran"))
    
    async def getAsync(self) -> datetime:
        return datetime.now(timezone("Asia/Tehran"))