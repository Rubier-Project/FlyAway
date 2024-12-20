from FlyClasses.fly import Fly, FlyObject, extractHashTags, run_pending
from quart import ( Quart, websocket, request, jsonify )
import json
import threading

quart = Quart(__name__)
fly_object = FlyObject()
fly = Fly()

async def isArray(data: str):
    try:
        return json.loads(data)
    except: return False

@quart.route("/getHashtagsFromText", methods=['POST'])
async def getHashtagsFromText():
    data: dict = await request.get_json()

    if "text" in data:
        return jsonify(
            await extractHashTags(data['text'])
        )
    else:
        return jsonify(
            {
                "status": "INVALID_INPUT"
            }
        )

@quart.websocket("/getTrends")
async def getTrends():
    data: dict = await websocket.receive_json()

    if not "auth_token" in data: await websocket.send_json({"status": "INVALID_INPUT"})

    user = await fly.getUserByAuth(data['auth_token'])
    if user['status'] == "OK":
        await websocket.send_json(
            await fly_object.getTrendTags()
        )
    else: await websocket.send_json(
        user
    )

@quart.websocket("/getExploreTwitts")
async def getExploreTwitts():
    data: dict = await websocket.receive_json()

    if not "auth_token" in data: await websocket.send_json({"status": "INVALID_INPUT"})

    user = await fly.getUserByAuth(data['auth_token'])
    if user['status'] == "OK":
        await websocket.send_json(
            await fly_object.getRandomTwitts()
        )
    else: await websocket.send_json(
        {
            "status": "INVALID_AUTH_TOKEN"
        }
    )

@quart.route("/signup", methods=['POST'])
async def signup():
    data: dict = await request.get_json()
    keys: list = list(data.keys())

    if not "fullname" in keys and not "username" in keys and not "phone_number" in keys: return jsonify({"status": "INVALID_INPUT"})
    if not "code" in keys:
        return jsonify(await fly.sendCode(data['phone_number']))
    else:
        accepted = await fly.acceptCode(
            data['phone_number'],
            data['code']
        )

        if accepted['status'] == "OK":
            return jsonify(
                await fly.add(
                    data['fullname'],
                    data['username'],
                    data['phone_number'],
                    data.get("bio", "")
                )
            )
        else:
            return jsonify(
                {
                    "status": "UNREGISTERED_CODE"
                }
            )

@quart.route("/signin", methods=['POST'])
async def signin():
    data: dict = await request.get_json()
    keys: list = list(data.keys())

    if not "phone_number" in keys: return jsonify({"status": "INVALID_INPUT"})
    if not "code" in keys:
        return jsonify(await fly.sendCode(data['phone_number']))
    else:

        accepted = await fly.acceptCode(
            data['phone_number'],
            data['code']
        )

        if accepted['status'] == "OK":
            return jsonify(
                await fly.getUserByPhoneNumber(
                    data['phone_number']
                )
            )
        else:
            return jsonify(
                {
                    "status": "UNREGISTERED_CODE"
                }
            )

@quart.route("/follow", methods=['POST'])
async def followUser():
    data = await request.get_json()

    if not "enc_data" in data and not "powkey" in data: return jsonify({"status": "INVALID_INPUT"})
    
    dec_data = await fly.fly_crypto.decrypt(data['enc_data'], data['powkey'])
    powkey = data['powkey']

    if dec_data['error'] == True:
        enced = await fly.fly_crypto.encrypt(json.dumps({"status": "INVALID_ENC" ,"message": dec_data['dec']}, ensure_ascii=False), data['powkey'])
        return jsonify({"enc_data": enced['enc'], "powkey": powkey})
    else:
        data = await isArray(dec_data['dec'])
        if not data == False:
            if 'auth_token' in data and 'following_user_id' in data:
                user = await fly.follow(
                    data['auth_token'],
                    data['following_user_id']
                )
                
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        user,
                        ensure_ascii=False
                    ),
                    powkey
                )

                return jsonify({"enc_data": enced['enc'], "powkey": powkey})
            else:
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        {
                            "status": "INVALID_INPUT"
                        }
                    ),
                    powkey
                )
                return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        else:
            enced = await fly.fly_crypto.encrypt(
                json.dumps(
                    {
                        "status": "INVALID_ENCODED_JSON"
                    }
                ),
                powkey
            )

            return jsonify({"enc_data": enced['enc'], "powkey": powkey})

@quart.route("/unfollow", methods=['POST'])
async def unfollowUser():
    data = await request.get_json()

    if not "enc_data" in data and not "powkey" in data: return jsonify({"status": "INVALID_INPUT"})
    
    dec_data = await fly.fly_crypto.decrypt(data['enc_data'], data['powkey'])
    powkey = data['powkey']

    if dec_data['error'] == True:
        enced = await fly.fly_crypto.encrypt(json.dumps({"status": "INVALID_ENC" ,"message": dec_data['dec']}, ensure_ascii=False), data['powkey'])
        return jsonify({"enc_data": enced['enc'], "powkey": powkey})
    else:
        data = await isArray(dec_data['dec'])
        if not data == False:
            if 'auth_token' in data and 'following_user_id' in data:
                user = await fly.unfollow(
                    data['auth_token'],
                    data['following_user_id']
                )
                
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        user,
                        ensure_ascii=False
                    ),
                    powkey
                )

                return jsonify({"enc_data": enced['enc'], "powkey": powkey})
            else:
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        {
                            "status": "INVALID_INPUT"
                        }
                    ),
                    powkey
                )
                return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        else:
            enced = await fly.fly_crypto.encrypt(
                json.dumps(
                    {
                        "status": "INVALID_ENCODED_JSON"
                    }
                ),
                powkey
            )

            return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        
@quart.route("/getMe", methods=['POST'])
async def getMe():
    data = await request.get_json()

    if not "enc_data" in data and not "powkey" in data: return jsonify({"status": "INVALID_INPUT"})
    
    dec_data = await fly.fly_crypto.decrypt(data['enc_data'], data['powkey'])
    powkey = data['powkey']

    if dec_data['error'] == True:
        enced = await fly.fly_crypto.encrypt(json.dumps({"status": "INVALID_ENC" ,"message": dec_data['dec']}, ensure_ascii=False), data['powkey'])
        return jsonify({"enc_data": enced['enc'], "powkey": powkey})
    else:
        data = await isArray(dec_data['dec'])
        if not data == False:
            if 'auth_token' in data:
                user = await fly.getUserByAuth(
                    data['auth_token']
                )
                
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        user,
                        ensure_ascii=False
                    ),
                    powkey
                )

                return jsonify({"enc_data": enced['enc'], "powkey": powkey})
            else:
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        {
                            "status": "INVALID_INPUT"
                        }
                    ),
                    powkey
                )
                return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        else:
            enced = await fly.fly_crypto.encrypt(
                json.dumps(
                    {
                        "status": "INVALID_ENCODED_JSON"
                    }
                ),
                powkey
            )

            return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        
@quart.route("/getUserById", methods=['POST'])
async def getUserById():
    data = await request.get_json()

    if not "enc_data" in data and not "powkey" in data: return jsonify({"status": "INVALID_INPUT"})
    
    dec_data = await fly.fly_crypto.decrypt(data['enc_data'], data['powkey'])
    powkey = data['powkey']

    if dec_data['error'] == True:
        enced = await fly.fly_crypto.encrypt(json.dumps({"status": "INVALID_ENC" ,"message": dec_data['dec']}, ensure_ascii=False), data['powkey'])
        return jsonify({"enc_data": enced['enc'], "powkey": powkey})
    else:
        data = await isArray(dec_data['dec'])
        if not data == False:
            if 'auth_token' in data and 'user_id' in data:
                user = await fly.getUserByAuth(
                    data['auth_token']
                )

                if user['status'] == "OK":
                    user = await fly.getUserByID(
                        data['user_id']
                    )

                    if "auth_token" in user['user']:del user['user']['auth_token']
                    if user['user']['settings']['hide_phone_number']:del user['user']['phone_number']
                    if not user['user']['settings']['show_my_followings']: del user['user']['followings']
                    if not user['user']['settings']['show_my_followers']: del user['user']['followers']

                    enced = await fly.fly_crypto.encrypt(
                        json.dumps(
                            user,
                            ensure_ascii=False
                        ),
                        powkey
                    )

                    return jsonify({"enc_data": enced['enc'], "powkey": powkey})
                else:
                    enced = await fly.fly_crypto.encrypt(
                        json.dumps(
                            user,
                            ensure_ascii=False
                        ),
                        powkey
                    )

                    return jsonify({"enc_data": enced['enc'], "powkey": powkey})
            else:
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        {
                            "status": "INVALID_INPUT"
                        }
                    ),
                    powkey
                )
                return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        else:
            enced = await fly.fly_crypto.encrypt(
                json.dumps(
                    {
                        "status": "INVALID_ENCODED_JSON"
                    }
                ),
                powkey
            )

            return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        
@quart.route("/addTwitt", methods=['POST'])
async def addTwitt():
    data = await request.get_json()

    if not "enc_data" in data and not "powkey" in data: return jsonify({"status": "INVALID_INPUT"})
    
    dec_data = await fly.fly_crypto.decrypt(data['enc_data'], data['powkey'])
    powkey = data['powkey']

    if dec_data['error'] == True:
        enced = await fly.fly_crypto.encrypt(json.dumps({"status": "INVALID_ENC" ,"message": dec_data['dec']}, ensure_ascii=False), data['powkey'])
        return jsonify({"enc_data": enced['enc'], "powkey": powkey})
    else:
        data: dict = await isArray(dec_data['dec'])
        if not data == False:
            if 'auth_token' in data and 'text' in data and 'type' in data:
                
                twitt = await fly_object.addTwitt(
                    data['auth_token'],
                    data['text'],
                    data['type'],
                    data.get("media", {})
                )

                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        twitt,
                        ensure_ascii=False
                    ),
                    powkey
                )

                return jsonify({'enc_data': enced['enc'], 'powkey': powkey})

            else:
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        {
                            "status": "INVALID_INPUT"
                        }
                    ),
                    powkey
                )
                return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        else:
            enced = await fly.fly_crypto.encrypt(
                json.dumps(
                    {
                        "status": "INVALID_ENCODED_JSON"
                    }
                ),
                powkey
            )

            return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        
@quart.route("/addTwittReply", methods=['POST'])
async def addTwittReply():
    data = await request.get_json()

    if not "enc_data" in data and not "powkey" in data: return jsonify({"status": "INVALID_INPUT"})
    
    dec_data = await fly.fly_crypto.decrypt(data['enc_data'], data['powkey'])
    powkey = data['powkey']

    if dec_data['error'] == True:
        enced = await fly.fly_crypto.encrypt(json.dumps({"status": "INVALID_ENC" ,"message": dec_data['dec']}, ensure_ascii=False), data['powkey'])
        return jsonify({"enc_data": enced['enc'], "powkey": powkey})
    else:
        data: dict = await isArray(dec_data['dec'])
        if not data == False:
            if 'auth_token' in data and 'text' in data and 'type' in data and 'to' in data and 'twitted_id' in data:
                
                twitt = await fly_object.addTwittReply(
                    data['auth_token'],
                    data['to'],
                    data['twitted_id'],
                    data['text'],
                    data['type'],
                    data.get("media", {})
                )

                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        twitt,
                        ensure_ascii=False
                    ),
                    powkey
                )

                return jsonify({'enc_data': enced['enc'], 'powkey': powkey})

            else:
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        {
                            "status": "INVALID_INPUT"
                        }
                    ),
                    powkey
                )
                return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        else:
            enced = await fly.fly_crypto.encrypt(
                json.dumps(
                    {
                        "status": "INVALID_ENCODED_JSON"
                    }
                ),
                powkey
            )

            return jsonify({"enc_data": enced['enc'], "powkey": powkey})

@quart.route("/removeTwitt", methods=['POST'])
async def removeTwitt():
    data = await request.get_json()

    if not "enc_data" in data and not "powkey" in data: return jsonify({"status": "INVALID_INPUT"})
    
    dec_data = await fly.fly_crypto.decrypt(data['enc_data'], data['powkey'])
    powkey = data['powkey']

    if dec_data['error'] == True:
        enced = await fly.fly_crypto.encrypt(json.dumps({"status": "INVALID_ENC" ,"message": dec_data['dec']}, ensure_ascii=False), data['powkey'])
        return jsonify({"enc_data": enced['enc'], "powkey": powkey})
    else:
        data: dict = await isArray(dec_data['dec'])
        if not data == False:
            if 'auth_token' in data and 'twitted_id' in data:
                
                twitt = await fly_object.removeTwitt(
                    data['auth_token'],
                    data['twitted_id']
                )

                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        twitt,
                        ensure_ascii=False
                    ),
                    powkey
                )

                return jsonify({'enc_data': enced['enc'], 'powkey': powkey})

            else:
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        {
                            "status": "INVALID_INPUT"
                        }
                    ),
                    powkey
                )
                return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        else:
            enced = await fly.fly_crypto.encrypt(
                json.dumps(
                    {
                        "status": "INVALID_ENCODED_JSON"
                    }
                ),
                powkey
            )

            return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        
@quart.route("/likeTwitt", methods=['POST'])
async def likeTwitt():
    data = await request.get_json()

    if not "enc_data" in data and not "powkey" in data: return jsonify({"status": "INVALID_INPUT"})
    
    dec_data = await fly.fly_crypto.decrypt(data['enc_data'], data['powkey'])
    powkey = data['powkey']

    if dec_data['error'] == True:
        enced = await fly.fly_crypto.encrypt(json.dumps({"status": "INVALID_ENC" ,"message": dec_data['dec']}, ensure_ascii=False), data['powkey'])
        return jsonify({"enc_data": enced['enc'], "powkey": powkey})
    else:
        data: dict = await isArray(dec_data['dec'])
        if not data == False:
            if 'auth_token' in data and 'to' in data and 'twitted_id' in data:
                
                twitt = await fly_object.likeTwitt(
                    data['auth_token'],
                    data['to'],
                    data['twitted_id']
                )

                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        twitt,
                        ensure_ascii=False
                    ),
                    powkey
                )

                return jsonify({'enc_data': enced['enc'], 'powkey': powkey})

            else:
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        {
                            "status": "INVALID_INPUT"
                        }
                    ),
                    powkey
                )
                return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        else:
            enced = await fly.fly_crypto.encrypt(
                json.dumps(
                    {
                        "status": "INVALID_ENCODED_JSON"
                    }
                ),
                powkey
            )

            return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        
@quart.route("/unlikeTwitt", methods=['POST'])
async def unlikeTwitt():
    data = await request.get_json()

    if not "enc_data" in data and not "powkey" in data: return jsonify({"status": "INVALID_INPUT"})
    
    dec_data = await fly.fly_crypto.decrypt(data['enc_data'], data['powkey'])
    powkey = data['powkey']

    if dec_data['error'] == True:
        enced = await fly.fly_crypto.encrypt(json.dumps({"status": "INVALID_ENC" ,"message": dec_data['dec']}, ensure_ascii=False), data['powkey'])
        return jsonify({"enc_data": enced['enc'], "powkey": powkey})
    else:
        data: dict = await isArray(dec_data['dec'])
        if not data == False:
            if 'auth_token' in data and 'to' in data and 'twitted_id' in data:
                
                twitt = await fly_object.unlikeTwitt(
                    data['auth_token'],
                    data['to'],
                    data['twitted_id']
                )

                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        twitt,
                        ensure_ascii=False
                    ),
                    powkey
                )

                return jsonify({'enc_data': enced['enc'], 'powkey': powkey})

            else:
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        {
                            "status": "INVALID_INPUT"
                        }
                    ),
                    powkey
                )
                return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        else:
            enced = await fly.fly_crypto.encrypt(
                json.dumps(
                    {
                        "status": "INVALID_ENCODED_JSON"
                    }
                ),
                powkey
            )

            return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        
@quart.route("/likeTwittReply", methods=['POST'])
async def likeTwittReply():
    data = await request.get_json()

    if not "enc_data" in data and not "powkey" in data: return jsonify({"status": "INVALID_INPUT"})
    
    dec_data = await fly.fly_crypto.decrypt(data['enc_data'], data['powkey'])
    powkey = data['powkey']

    if dec_data['error'] == True:
        enced = await fly.fly_crypto.encrypt(json.dumps({"status": "INVALID_ENC" ,"message": dec_data['dec']}, ensure_ascii=False), data['powkey'])
        return jsonify({"enc_data": enced['enc'], "powkey": powkey})
    else:
        data: dict = await isArray(dec_data['dec'])
        if not data == False:
            if 'auth_token' in data and 'to' in data and 'twitted_id' in data and 'twitted_reply_id' in data:
                
                twitt = await fly_object.likeTwittReply(
                    data['auth_token'],
                    data['to'],
                    data['twitted_id'],
                    data['twitted_reply_id']
                )

                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        twitt,
                        ensure_ascii=False
                    ),
                    powkey
                )

                return jsonify({'enc_data': enced['enc'], 'powkey': powkey})

            else:
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        {
                            "status": "INVALID_INPUT"
                        }
                    ),
                    powkey
                )
                return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        else:
            enced = await fly.fly_crypto.encrypt(
                json.dumps(
                    {
                        "status": "INVALID_ENCODED_JSON"
                    }
                ),
                powkey
            )

            return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        
@quart.route("/unlikeTwittReply", methods=['POST'])
async def unlikeTwittReply():
    data = await request.get_json()

    if not "enc_data" in data and not "powkey" in data: return jsonify({"status": "INVALID_INPUT"})
    
    dec_data = await fly.fly_crypto.decrypt(data['enc_data'], data['powkey'])
    powkey = data['powkey']

    if dec_data['error'] == True:
        enced = await fly.fly_crypto.encrypt(json.dumps({"status": "INVALID_ENC" ,"message": dec_data['dec']}, ensure_ascii=False), data['powkey'])
        return jsonify({"enc_data": enced['enc'], "powkey": powkey})
    else:
        data: dict = await isArray(dec_data['dec'])
        if not data == False:
            if 'auth_token' in data and 'to' in data and 'twitted_id' in data and 'twitted_reply_id' in data:
                
                twitt = await fly_object.unlikeTwittReply(
                    data['auth_token'],
                    data['to'],
                    data['twitted_id'],
                    data['twitted_reply_id']
                )

                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        twitt,
                        ensure_ascii=False
                    ),
                    powkey
                )

                return jsonify({'enc_data': enced['enc'], 'powkey': powkey})

            else:
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        {
                            "status": "INVALID_INPUT"
                        }
                    ),
                    powkey
                )
                return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        else:
            enced = await fly.fly_crypto.encrypt(
                json.dumps(
                    {
                        "status": "INVALID_ENCODED_JSON"
                    }
                ),
                powkey
            )

            return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        
@quart.route("/updateProfile", methods=['POST'])
async def updateProfile():
    data = await request.get_json()

    if not "enc_data" in data and not "powkey" in data: return jsonify({"status": "INVALID_INPUT"})
    
    dec_data = await fly.fly_crypto.decrypt(data['enc_data'], data['powkey'])
    powkey = data['powkey']

    if dec_data['error'] == True:
        enced = await fly.fly_crypto.encrypt(json.dumps({"status": "INVALID_ENC" ,"message": dec_data['dec']}, ensure_ascii=False), data['powkey'])
        return jsonify({"enc_data": enced['enc'], "powkey": powkey})
    else:
        data: dict = await isArray(dec_data['dec'])
        if not data == False:
            if 'auth_token' in data:
                
                user = await fly.update(
                    data['auth_token'],
                    data.get("fullname", ""),
                    data.get("username", ""),
                    data.get("bio", ""),
                    data.get("profile_photo", ""),
                    data.get("hide_phone_number", None),
                    data.get("others_can_repost_my_twitts", None),
                    data.get("show_my_followings", None),
                    data.get("show_my_followers", None)
                )

                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        user,
                        ensure_ascii=False
                    ),
                    powkey
                )

                return jsonify({'enc_data': enced['enc'], 'powkey': powkey})

            else:
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        {
                            "status": "INVALID_INPUT"
                        }
                    ),
                    powkey
                )
                return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        else:
            enced = await fly.fly_crypto.encrypt(
                json.dumps(
                    {
                        "status": "INVALID_ENCODED_JSON"
                    }
                ),
                powkey
            )

            return jsonify({"enc_data": enced['enc'], "powkey": powkey})

@quart.route("/deleteAccount", methods=['POST'])
async def deleteAccount():
    data = await request.get_json()

    if not "enc_data" in data and not "powkey" in data: return jsonify({"status": "INVALID_INPUT"})

    dec_data = await fly.fly_crypto.decrypt(data['enc_data'], data['powkey'])
    powkey = data['powkey']

    if dec_data['error'] == True:
        enced = await fly.fly_crypto.encrypt(json.dumps({"status": "INVALID_ENC" ,"message": dec_data['dec']}, ensure_ascii=False), data['powkey'])
        return jsonify({"enc_data": enced['enc'], "powkey": powkey})
    else:
        data: dict = await isArray(dec_data['dec'])
        if not data == False:
            if 'auth_token' in data:
                user = await fly.delete(
                    data['auth_token']
                )

                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        user,
                        ensure_ascii=False
                    ),
                    powkey
                )

                return jsonify({'enc_data': enced['enc'], 'powkey': powkey})

            else:
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        {
                            "status": "INVALID_INPUT"
                        }
                    ),
                    powkey
                )
                return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        else:
            enced = await fly.fly_crypto.encrypt(
                json.dumps(
                    {
                        "status": "INVALID_ENCODED_JSON"
                    }
                ),
                powkey
            )

            return jsonify({"enc_data": enced['enc'], "powkey": powkey})
        
@quart.websocket("/getMeHandshake")
async def getMeHandshake():
    data = await websocket.receive_json()

    if not "enc_data" in data and not "powkey" in data: await websocket.send_json({"status": "INVALID_INPUT"})
    
    dec_data = await fly.fly_crypto.decrypt(data['enc_data'], data['powkey'])
    powkey = data['powkey']

    if dec_data['error'] == True:
        enced = await fly.fly_crypto.encrypt(json.dumps({"status": "INVALID_ENC" ,"message": dec_data['dec']}, ensure_ascii=False), data['powkey'])
        await websocket.send_json({"enc_data": enced['enc'], "powkey": powkey})
    else:
        data = await isArray(dec_data['dec'])
        if not data == False:
            if 'auth_token' in data:
                user = await fly.getUserByAuth(
                    data['auth_token']
                )
                
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        user,
                        ensure_ascii=False
                    ),
                    powkey
                )

                await websocket.send_json({"enc_data": enced['enc'], "powkey": powkey})
            else:
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        {
                            "status": "INVALID_INPUT"
                        }
                    ),
                    powkey
                )
                await websocket.send_json({"enc_data": enced['enc'], "powkey": powkey})
        else:
            enced = await fly.fly_crypto.encrypt(
                json.dumps(
                    {
                        "status": "INVALID_ENCODED_JSON"
                    }
                ),
                powkey
            )

            await websocket.send_json({"enc_data": enced['enc'], "powkey": powkey})

@quart.websocket("/getUserTwitts")
async def getUserTwitts():
    data = await websocket.receive_json()

    if not "enc_data" in data and not "powkey" in data: await websocket.send_json({"status": "INVALID_INPUT"})
    
    dec_data = await fly.fly_crypto.decrypt(data['enc_data'], data['powkey'])
    powkey = data['powkey']

    if dec_data['error'] == True:
        enced = await fly.fly_crypto.encrypt(json.dumps({"status": "INVALID_ENC" ,"message": dec_data['dec']}, ensure_ascii=False), data['powkey'])
        await websocket.send_json({"enc_data": enced['enc'], "powkey": powkey})
    else:
        data = await isArray(dec_data['dec'])
        if not data == False:
            if 'auth_token' in data and 'user_id' in data:
                user = await fly.getUserByAuth(
                    data['auth_token']
                )

                if user['status'] == "OK":

                    from_user = await fly.getUserByID(data['user_id'])

                    if from_user['status'] == "OK":
                 
                        enced = await fly.fly_crypto.encrypt(
                            json.dumps(
                                {"status": "OK", "twitts": from_user['user']['twts']},
                                ensure_ascii=False
                            ),
                            powkey
                        )

                        await websocket.send_json({"enc_data": enced['enc'], "powkey": powkey})
                    else: await websocket.send_json(from_user)
                else: await websocket.send_json(user)
            else:
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        {
                            "status": "INVALID_INPUT"
                        }
                    ),
                    powkey
                )
                await websocket.send_json({"enc_data": enced['enc'], "powkey": powkey})
        else:
            enced = await fly.fly_crypto.encrypt(
                json.dumps(
                    {
                        "status": "INVALID_ENCODED_JSON"
                    }
                ),
                powkey
            )

            await websocket.send_json({"enc_data": enced['enc'], "powkey": powkey})

@quart.websocket("/getUserByIdHandshake")
async def getUserByIdHandshake():
    data = await websocket.receive_json()

    if not "enc_data" in data and not "powkey" in data: await websocket.send_json({"status": "INVALID_INPUT"})
    
    dec_data = await fly.fly_crypto.decrypt(data['enc_data'], data['powkey'])
    powkey = data['powkey']

    if dec_data['error'] == True:
        enced = await fly.fly_crypto.encrypt(json.dumps({"status": "INVALID_ENC" ,"message": dec_data['dec']}, ensure_ascii=False), data['powkey'])
        await websocket.send_json({"enc_data": enced['enc'], "powkey": powkey})
    else:
        data = await isArray(dec_data['dec'])
        if not data == False:
            if 'auth_token' in data and 'user_id' in data:
                user = await fly.getUserByAuth(
                    data['auth_token']
                )

                if user['status'] == "OK":

                    from_user = await fly.getUserByID(data['user_id'])

                    if from_user['status'] == "OK":
                        
                        if "auth_token" in user['user']:del user['user']['auth_token']
                        if from_user['user']['settings']['hide_phone_number']:del from_user['user']['phone_number']
                        if not from_user['user']['settings']['show_my_followings']: del from_user['user']['followings']
                        if not from_user['user']['settings']['show_my_followers']: del from_user['user']['followers']
                 
                        enced = await fly.fly_crypto.encrypt(
                            json.dumps(
                                from_user,
                                ensure_ascii=False
                            ),
                            powkey
                        )

                        await websocket.send_json({"enc_data": enced['enc'], "powkey": powkey})
                    else: await websocket.send_json(from_user)
                else: await websocket.send_json(user)
            else:
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        {
                            "status": "INVALID_INPUT"
                        }
                    ),
                    powkey
                )
                await websocket.send_json({"enc_data": enced['enc'], "powkey": powkey})
        else:
            enced = await fly.fly_crypto.encrypt(
                json.dumps(
                    {
                        "status": "INVALID_ENCODED_JSON"
                    }
                ),
                powkey
            )

            await websocket.send_json({"enc_data": enced['enc'], "powkey": powkey})

@quart.websocket("/repostTwitt")
async def repostTwitt():
    data = await websocket.receive_json()

    if not "enc_data" in data and not "powkey" in data: await websocket.send_json({"status": "INVALID_INPUT"})
    
    dec_data = await fly.fly_crypto.decrypt(data['enc_data'], data['powkey'])
    powkey = data['powkey']

    if dec_data['error'] == True:
        enced = await fly.fly_crypto.encrypt(json.dumps({"status": "INVALID_ENC" ,"message": dec_data['dec']}, ensure_ascii=False), data['powkey'])
        await websocket.send_json({"enc_data": enced['enc'], "powkey": powkey})
    else:
        data = await isArray(dec_data['dec'])
        if not data == False:
            if 'auth_token' in data and 'from_user_id' in data and 'twitted_id' in data:
                repost = await fly_object.repostTwitt(data['auth_token'], data['from_user_id'], data['twitted_id'])
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        repost,
                        ensure_ascii=False
                    ),
                    powkey
                )

                await websocket.send_json({"enc_data": enced['enc'], "powkey": powkey})

            else:
                enced = await fly.fly_crypto.encrypt(
                    json.dumps(
                        {
                            "status": "INVALID_INPUT"
                        }
                    ),
                    powkey
                )
                await websocket.send_json({"enc_data": enced['enc'], "powkey": powkey})
        else:
            enced = await fly.fly_crypto.encrypt(
                json.dumps(
                    {
                        "status": "INVALID_ENCODED_JSON"
                    }
                ),
                powkey
            )

            await websocket.send_json({"enc_data": enced['enc'], "powkey": powkey})

if __name__ == "__main__":
    threading.Thread(target=run_pending).start()
    quart.run(
        "0.0.0.0",
        3000
    )
