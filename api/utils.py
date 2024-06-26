import hashlib
import hmac


def generate_hmac(secret, message):
    return hmac.new(secret.encode(), message.encode(), hashlib.sha1).hexdigest()
