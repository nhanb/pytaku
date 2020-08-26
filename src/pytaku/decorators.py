from functools import wraps

from flask import jsonify, request

from .persistence import verify_token


def process_token(required=True):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.cookies.get("token")
            if not token:
                if required:
                    return (
                        jsonify({"message": "Missing 'token' cookie."}),
                        401,
                    )
                else:
                    request.token = None
                    request.user_id = None
                    return f(*args, **kwargs)

            user_id = verify_token(token)
            if user_id is None:
                return jsonify({"message": "Invalid token."}), 401

            request.token = token
            request.user_id = user_id

            return f(*args, **kwargs)

        return decorated_function

    return decorator
