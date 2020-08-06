from functools import wraps

from flask import redirect, request, session, url_for

from .persistence import read


def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user") is None:
            return redirect(url_for("auth_view", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def trigger_has_read(f):
    """
    Augments a view with the ability to mark a chapter as read if there's a
    `?has_read=<chapter_id>` url param.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        assert "site" in kwargs  # only use on site-specific views
        has_read_chapter_id = request.args.get("has_read")
        if has_read_chapter_id:
            if session.get("user"):
                read(session["user"]["id"], kwargs["site"], has_read_chapter_id)
                return redirect(request.url[: request.url.rfind("?")])
        return f(*args, **kwargs)

    return decorated_function
