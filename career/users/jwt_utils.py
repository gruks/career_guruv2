import jwt
from datetime import datetime, timedelta
from flask import current_app

def generate_access_token(user_id, expires_in=3600):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in)
    }
    secret = current_app.config.get('SECRET_KEY', 'supersecret')
    return jwt.encode(payload, secret, algorithm='HS256')

def verify_access_token(token):
    secret = current_app.config.get('SECRET_KEY', 'supersecret')
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None