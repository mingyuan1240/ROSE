import time
import datetime
import json
import base64
import hmac
from hashlib import sha1 as sha


accessKeyId = 'LTAITVHjncC57cMb'
accessKeySecret = 'ry9ga9d729OryK1OvhECu6ehdhwLeH'
host = 'http://rosewebsite.oss-cn-shanghai.aliyuncs.com'
expire_time = 6000

def get_iso_8601(expire):
    gmt = datetime.datetime.fromtimestamp(expire).isoformat()
    gmt += 'Z'
    return gmt

def get_token():
    now = int(time.time())
    expire_syncpoint  = now + expire_time
    expire = get_iso_8601(expire_syncpoint)

    policy_dict = {}
    policy_dict['expiration'] = expire
    condition_array = []
    array_item = ["content-length-range", 0, 1048576000]
    condition_array.append(array_item)
    policy_dict['conditions'] = condition_array
    policy = json.dumps(policy_dict).strip()
    policy_encode = base64.b64encode(bytes(policy,'utf-8'))
    h = hmac.new(bytes(accessKeySecret,'utf8'), policy_encode, sha)
    sign_result = str(base64.b64encode(h.digest()),'utf-8').strip()

    token_dict = {}
    token_dict['accessid'] = accessKeyId
    token_dict['host'] = host
    token_dict['policy'] = str(policy_encode,'utf8')
    token_dict['signature'] = sign_result
    token_dict['expire'] = expire_syncpoint
    return token_dict
