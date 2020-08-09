from functools import wraps

from flask import redirect, request, session, url_for

from .persistence import read, unread


def ensure_session_version(f, CURRENT_VERSION=1):
    """
    Increment CURRENT_VERSION to nuke all current sessions.
    Useful for when I try to change session structure or something. Maybe.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (
            not session.get("version")
            or not isinstance(session["version"], int)
            or session["version"] < CURRENT_VERSION
        ):
            session.clear()
            session["version"] = CURRENT_VERSION
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function


def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user") is None:
            return redirect(url_for("auth_view", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def toggle_has_read(f):
    """
    Augments a view with the ability to toggle a chapter's read status if there's a
    `?has_read=<chapter_id>` url param.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        assert "site" in kwargs
        assert "title_id" in kwargs
        has_read_chapter_id = request.args.get("has_read")
        unread_chapter_id = request.args.get("unread")
        assert not (has_read_chapter_id and unread_chapter_id)  # can't do both

        if session.get("user"):
            if has_read_chapter_id:
                read(
                    session["user"]["id"],
                    kwargs["site"],
                    kwargs["title_id"],
                    has_read_chapter_id,
                )
                return redirect(request.url[: request.url.rfind("?")])
            elif unread_chapter_id:
                unread(
                    session["user"]["id"],
                    kwargs["site"],
                    kwargs["title_id"],
                    unread_chapter_id,
                )
                return redirect(request.url[: request.url.rfind("?")])
        return f(*args, **kwargs)

    return decorated_function
