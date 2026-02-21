from aiohttp.web import json_response as aiohttp_json_response
from aiohttp.web_response import Response
from functools import wraps
from aiohttp.web_exceptions import HTTPForbidden

def json_response(data: dict | None = None, status: str = "ok") -> Response:
    if data is None:
        data = {}

    return aiohttp_json_response(
        data={
            "status": status,
            "data": data,
        }
    )


def error_json_response(
    http_status: int,
    status: str = "error",
    message: str | None = None,
    data: dict | None = None,
):
    data = {} if data is None else data
    message = "" if message is None else message
    return aiohttp_json_response(
        status=http_status,
        data={
            "status": status,
            "message": str(message),
            "data": data
        }
    )


def auth_required(handler):
    @wraps(handler)
    async def wrapper(view, *args, **kwargs):
        admin_id = view.check_cookie(
            view.request.cookies, 
            view.request.app.config.session.key
        )
        admin = await view.request.app.store.admins.get_by_id(admin_id)
        if not admin:
            raise HTTPForbidden(reason="Admin not found")
        
        # Сохраняем админа в request
        view.request.admin = admin
        return await handler(view, *args, **kwargs)
    return wrapper