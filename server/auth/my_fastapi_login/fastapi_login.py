import typing
from datetime import timedelta, datetime
from typing import Callable, Awaitable, Union
from typing import Optional, Tuple
import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from starlette.datastructures import Secret
from starlette.requests import Request
from starlette.responses import Response
from fastapi.exceptions import HTTPException
from server.auth.my_fastapi_login.exceptions import InvalidCredentialsException
from starlette.status import HTTP_401_UNAUTHORIZED


def get_authorization_scheme_param(authorization_header_value: str) -> Tuple[str, str]:
    """
    从fastapi的oauth2的auth拷贝过来的，把异步版本改为了同步版本
    :param authorization_header_value:
    :return:
    """
    if not authorization_header_value:
        return "", ""
    scheme, _, param = authorization_header_value.partition(" ")
    return scheme, param


class LoginManager(OAuth2PasswordBearer):
    """
    改造了github上的fast_api_login,把async版本改成了sync版本
    """
    def __init__(self, secret: str, tokenUrl: str, algorithm="HS256", use_cookie=False, use_header=True):
        """
        :param str secret: Secret key used to sign and decrypt the JWT
        :param str algorithm: Should be "HS256" or "RS256" used to decrypt the JWT
        :param str tokenUrl: The url where the user can login to get the token
        :param bool use_cookie: Set if cookies should be checked for the token
        :param bool use_header: Set if headers should be checked for the token
        """
        if use_cookie is False and use_header is False:
            raise Exception("use_cookie and use_header are both False one of them needs to be True")
        self.secret = Secret(secret)
        self._user_callback = None
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"])
        # this is not mandatory as they user may want to user their own
        # function to get the token and pass it to the get_current_user method
        self.tokenUrl = tokenUrl
        self.oauth_scheme = None
        self._not_authenticated_exception = None

        self.use_cookie = use_cookie
        self.use_header = use_header
        self.cookie_name = 'access-token'

        super().__init__(tokenUrl=tokenUrl, auto_error=True)

    @property
    def not_authenticated_exception(self):
        return self._not_authenticated_exception

    @not_authenticated_exception.setter
    def not_authenticated_exception(self, value: Exception):
        """
        Setter for the Exception which raises when the user is not authenticated

        :param Exception value: The Exception you want to raise
        """
        assert issubclass(value, Exception)  # noqa
        self._not_authenticated_exception = value
        # change auto error setting on OAuth2PasswordBearer
        self.auto_error = False

    def user_loader(self, callback: Union[Callable, Awaitable]) -> Union[Callable, Awaitable]:
        """
        This sets the callback to retrieve the user.
        The function should take an unique identifier like an email
        and return the user object or None.
        :param Callable or Awaitable callback: The callback which returns the user
        :return: The callback
        """
        self._user_callback = callback
        return callback

    def get_current_user(self, token: str):
        """
        This decodes the jwt based on the secret and on the algorithm
        set on the LoginManager.
        If the token is correctly formatted and the user is found
        the user is returned else this raises a `fastapi.HTTPException`

        :param str token: The encoded jwt token
        :return: The user object returned by `self._user_callback`
        :raise: HTTPException if the token is invalid or the user is not found
        """
        try:
            payload = jwt.decode(
                token,
                str(self.secret),
                algorithms=[self.algorithm]
            )
            # the identifier should be stored under the sub (subject) key
            user_identifier = payload.get('sub')
            if user_identifier is None:
                raise InvalidCredentialsException
        # This includes all errors raised by pyjwt
        except jwt.PyJWTError:
            raise InvalidCredentialsException

        user = self._load_user(user_identifier)

        if user is None:
            raise InvalidCredentialsException

        return user

    def _load_user(self, identifier: typing.Any):
        """
        This loads the user using the user_callback

        :param Any identifier: The identifier the user callback takes
        :return: The user object or None
        :raises: Exception if the user_loader has not been set
        """
        if self._user_callback is None:
            raise Exception(
                "Missing user_loader callback"
            )

        user = self._user_callback(identifier)

        return user

    def create_access_token(self, *, data: dict, expires_delta: timedelta = None) -> str:
        """
        Helper function to create the encoded access token using
        the provided secret and the algorithm of the LoginManager instance

        :param dict data: The data which should be stored in the token
        :param  timedelta expires_delta: An optional timedelta in which the token expires.
            Defaults to 15 minutes
        :return: The encoded JWT with the data and the expiry. The expiry is
            available under the 'exp' key
        """

        to_encode = data.copy()

        if expires_delta:
            expires_in = datetime.utcnow() + expires_delta
        else:
            # default to 15 minutes expiry times
            expires_in = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({'exp': expires_in})
        encoded_jwt = jwt.encode(to_encode, str(self.secret), self.algorithm)
        # decode here decodes the byte str to a normal str not the token
        return encoded_jwt.decode()

    def set_cookie(self, response: Response, token: str) -> None:
        """
        Utility function to handle cookie setting on the response

        :param response: The response which is send back
        :param token: The created JWT
        """
        response.set_cookie(
            key=self.cookie_name,
            value=token,
            httponly=True
        )

    def _token_from_cookie(self, request: Request) -> typing.Optional[str]:
        """
        Checks the requests cookies for cookies with the name `self.cookie_name`

        :param Request request: The request to the route, normally filled in automatically
        :return: The access token found in the cookies of the request or None
        """
        token = request.cookies.get(self.cookie_name)

        if not token and self.auto_error:
            # this is the standard exception as raised
            # by the parent class
            raise InvalidCredentialsException

        else:
            return token if token else None

    def sync_super_call(self, request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param

    def __call__(self, request: Request):
        """
        Provides the functionality to act as a Dependency

        :param Request request: The incoming request, this is set automatically
            by FastAPI
        :return: The user object or None
        :raises: The not_authenticated_exception if set by the user
        """
        token = None
        if self.use_cookie:
            token = self._token_from_cookie(request)

        if token is None and self.use_header:
            token = self.sync_super_call(request)

        if token is not None:
            return self.get_current_user(token)

        # No token is present in the request and no Exception has been raised (auto_error=False)
        raise self.not_authenticated_exception
