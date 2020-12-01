from fastapi import APIRouter
from djadmin.djadmin.settings import SECRET_KEY
from server.auth.my_fastapi_login import LoginManager
from django.contrib import auth
from django.contrib.auth.models import User as DjangoUser
from djadmin.eecs.models import UserRole, Role
from fastapi.security import OAuth2PasswordRequestForm
from server.auth.my_fastapi_login.exceptions import InvalidCredentialsException
from fastapi import Depends
from datetime import timedelta
from pydantic import BaseModel, Field
from typing import List, Any

manager = LoginManager(SECRET_KEY, tokenUrl='/auth/token')


@manager.user_loader
def load_user(username: str) -> DjangoUser:
    """
    从Django admin中加载用户
    :param username: 用户名
    :return: 用户对象
    """
    user = DjangoUser.objects.get(username=username)
    return user


login_router = APIRouter()


class LoginResult(BaseModel):
    """
    登陆请求结果
    """
    code: int = Field(title="代码")
    auth_token: str = Field(title="token,前端应该存在本地")
    token_type: str = Field(title="token类型")


@login_router.post('/token', response_model=LoginResult)
def login(data: OAuth2PasswordRequestForm = Depends()):
    """
    处理登陆请求的逻辑，请求字段中必须包含username和password字段，若登陆成功则返回一个access_token和token_type,
    目前使用Bearer type的方式做token认证
    :param data: fastapi定义的OAuth2表格格式
    :return:
    """
    username = data.username
    password = data.password
    django_user = auth.authenticate(username=username, password=password)
    if not django_user:
        raise InvalidCredentialsException
    username = django_user.username
    access_token = manager.create_access_token(
        data=dict(sub=username), expires_delta=timedelta(hours=12)
    )  # 12小时到期
    return {'code': 20000, 'auth_token': access_token, 'token_type': 'bearer'}


class LogoutResult(BaseModel):
    """
    登出请求结果
    """
    code: int = Field(title="代码")


@login_router.post('/logout')
def logout(user=Depends(manager)):
    """
    登出
    :param user:
    :return:
    """
    return {'code': 20000}


@login_router.get('/protected')
def protected_route(user=Depends(manager)):
    """
    登陆的用户访问会返回用户名，未登陆的用户会返回422错误{"detail": "Not authenticated"}
    并且报401错误
    :param user: 用户对象
    :return: 用户名
    """
    return user.username


class UserInfo(BaseModel):
    code: int = Field(title="代码")
    roles: List[str] = Field(title="角色")
    name: str = Field(title="名字")
    avatar: str = Field(title="头像")
    introduction: str = Field(title="介绍")


@login_router.get('/user/info', response_model=UserInfo)
def get_user_info(user=Depends(manager)):
    roles = [each.role.name for each in UserRole.objects.filter(user=user)]
    return {
        "code": 20000,
        "roles": roles,
        "name": user.username,
        "avatar": "https://gitee.com/static/images/logo-black.svg?t=158106664",
        "introduction": ""
    }
