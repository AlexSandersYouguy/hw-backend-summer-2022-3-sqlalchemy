import jwt
import uuid
from datetime import datetime, timedelta
from aiohttp.web_exceptions import HTTPUnauthorized, HTTPForbidden
from typing import Optional
from aiohttp.web_response import Response

class AuthRequiredMixin:
    
    def _create_token(self, admin_id: int, session_key: str) -> str:
        """Создает JWT токен с session.key"""
        payload = {
            'admin_id': admin_id,
            'uuid': str(uuid.uuid4()),
            'exp': datetime.now() + timedelta(hours=1)
        }
        return jwt.encode(
            payload,
            session_key, 
            algorithm='HS256'
        )
    
    def check_cookie(self, cookies: dict, session_key: str) -> Optional[int]:
        """
        Проверяет JWT токен в куке с session_key
        Возвращает admin_id или выбрасывает исключение
        """
        try:
            raw_token = cookies["user_token"]
            if not raw_token:
                raise HTTPUnauthorized(reason="No cookie provided")
            
            payload = jwt.decode(
                raw_token,
                session_key, 
                algorithms=['HS256']
            )
            
            admin_id = payload.get('admin_id')
            if not admin_id:
                raise HTTPForbidden(reason="Invalid token payload")
            
            return admin_id
            
        except jwt.ExpiredSignatureError:
            raise HTTPForbidden(reason="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPForbidden(reason="Invalid token")
        except KeyError:
            raise HTTPUnauthorized(reason="No cookie")
        except Exception as e:
            print(f"Cookie check error: {e}")
            raise HTTPForbidden(reason="Invalid token")
    
    def set_auth_cookie(self, response: Response, admin_id: int, session_key: str):
        """Устанавливает JWT куку"""
        token = self._create_token(admin_id, session_key)
        response.set_cookie(
            "user_token",
            token,
            httponly=True,
            secure=False, 
            samesite="Lax",
            max_age=3600, 
            path="/"
        )
    
    def delete_auth_cookie(self, response: Response):
        """Удаляет куку"""
        response.del_cookie("user_token", path="/")