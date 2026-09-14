# -*- coding: utf-8 -*-
from functools import wraps

from flask import session, redirect, url_for, request


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapped
