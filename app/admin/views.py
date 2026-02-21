from app.web.app import View
from app.web.utils import json_response, auth_required
from aiohttp_apispec import request_schema, response_schema
from app.admin.schemes import AdminSchema
from app.web.schemes import OkResponseSchema
from aiohttp.web_exceptions import HTTPForbidden
from app.web.mixins import AuthRequiredMixin

class AdminLoginView(View, AuthRequiredMixin):
    @request_schema(AdminSchema)
    @response_schema(OkResponseSchema, 200)
    async def post(self):
        data = self.request["data"]
        admin = await self.request.app.store.admins.get_by_email(data["email"])
        
        if not admin:
            raise HTTPForbidden(reason="Invalid credentials")
        
        response = json_response(data={
            "id": admin.id,
            "email": admin.email
        })
        
        self.set_auth_cookie(response, admin.id, self.request.app.config.session.key)
        
        return response
        


class AdminCurrentView(View, AuthRequiredMixin):
    @auth_required
    async def get(self):
        return json_response(data={
            "id": self.request.admin.id,
            "email": self.request.admin.email
        })