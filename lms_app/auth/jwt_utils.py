#Having json web tokens for encoding and verfication of roles(helper file)#
import jwt
from datetime import datetime, timedelta
from flask import current_app, request, jsonify
from functools import wraps

def build_token(user_id, role):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    return token

def confirm_token():
    http_auth_header = request.headers.get("Authorization")
    
    if not http_auth_header:
        return None, jsonify({"error": "Authorization header missing"}), 401
    
    try:
        token = http_auth_header.split(" ")[1]
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        return payload, None, None
    
    except jwt.ExpiredSignatureError:
        return None, jsonify({"error": "Token expired"}), 401
    
    except jwt.InvalidTokenError:
        return None, jsonify({"error": "Token invalid"}), 401

#Decorator for the internal route switching#
def call_auth(role=None):
    def func_mod(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            payload, error_response, status = confirm_token()
            
            if error_response:
                return error_response, status
            
            if role and payload["role"] != role:
                return jsonify({"error": "Banned"}), 403
            
            return f(payload, *args, **kwargs)
        return wrapper
    return func_mod