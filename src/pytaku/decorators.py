from functools import wraps

from flask import redirect, request, session, url_for


def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user") is None:
            return redirect(url_for("auth_view", next=request.url))
        return f(*args, **kwargs)

    return decorated_function
