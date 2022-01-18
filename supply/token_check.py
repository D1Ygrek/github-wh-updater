import hmac
import hashlib

def create_hash(body, secret):
    digest_hex = hmac.new(key = secret.app_secret.encode('utf-8'), msg = body, digestmod = hashlib.sha256).hexdigest()
    return 'sha256='+digest_hex