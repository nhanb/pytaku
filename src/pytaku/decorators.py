from functools import wraps

from flask import jsonify, render_template, request

from mangoapi.exceptions import (
    SourceSite5xxError,
    SourceSiteResponseError,
    SourceSiteTimeoutError,
    SourceSiteUnexpectedError,
)

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


SOURCE_SITE_ERRORS = {
    SourceSiteTimeoutError: {
        "code": "source_site_timeout",
        "message": "Source site took too long to respond. Try again later.",
    },
    SourceSite5xxError: {
        "code": "source_site_5xx",
        "message": "Source site crapped the bed. Try again later.",
    },
    SourceSiteUnexpectedError: {
        "code": "source_site_unexpected",
        "message": "Unexpected error when requesting source site.",
    },
}


def handle_source_site_errors(format="json"):
    assert format in ("json", "html"), f"{format} ain't no format I ever heard of!"

    def outer_func(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except SourceSiteResponseError as err:
                resp = SOURCE_SITE_ERRORS[err.__class__]
                resp["detail"] = err.__dict__
                if format == "json":
                    return jsonify(resp), 500
                elif format == "html":
                    return render_template("error.html", **resp), 500

        return decorated_function

    return outer_func
