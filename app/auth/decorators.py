"""Custom decorators for access control."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from flask import abort
from flask.typing import ResponseReturnValue
from flask_login import current_user, login_required

P = ParamSpec("P")
R = TypeVar("R", bound=ResponseReturnValue)


def admin_required(view: Callable[P, R]) -> Callable[P, R]:  # noqa: UP047
    @wraps(view)
    @login_required
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        if current_user.role != "admin":
            abort(403)
        return view(*args, **kwargs)

    return wrapper


__all__ = ["admin_required"]
