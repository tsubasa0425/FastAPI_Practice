'''
OAuth2.0的授权模式

- 授权码授权模式(Authorization Code Grant)
- 隐式授权模式(Implicit Grant)
- **密码授权模式(Resource Owner Password Credentials Grant)**
- 客户端凭证授权模式(Client Credentials Grant)

'''

from fastapi import APIRouter

from pydantic_tutorial import user

app06 = APIRouter()

''' ************** 1. OAuth2 密码模式和 FastAPI 的 OAuth2PasswordBearer ************** '''

"""
OAuth2PasswordBearer是接收URL作为参数的一个类：客户端会向该URL发送username和password参数，然后得到一个Token值
OAuth2PasswordBearer并不会创建相应的URL路径操作，只是指明客户端用来请求Token的URL地址
当请求到来的时候，FastAPI会检查请求的Authorization头信息，如果没有找到Authorization头信息，或者头信息的内容不是Bearer token，它会返回401状态码(UNAUTHORIZED)
"""

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/chapter06/token')   # 请求Token的URL地址 http://127.0.0.1:8000/chapter06/token

@app06.get('/oauth2_password_bearer')
async def oauth2_password_bearer(token: str = Depends(oauth2_schema)):
    return {'token': token}


''' ************** 2. 基于 Password 和 Bearer token 的 OAuth2 认证 ************** '''

from pydantic import BaseModel
from typing import Optional

fake_users_db = {
    "john snow": {
        "username": "john snow",
        "full_name": "John Snow",
        "email": "johnsnow@example.com",
        "hashed_password": "fakehashedsecret",  # 已加密的密码
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

# 给密码哈希加密
def fake_hash_password(password: str):
    return "fakehashed" + password


class User(BaseModel):
    username: str
    full_name: Optional[str]=None
    email: Optional[str]=None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str

# 获取用户
def get_user(db, username:str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


# 解码校验token
def fake_decode_token(token:str):
    user = get_user(fake_users_db, token)
    return user



@app06.post('/token')
async def login(form_data: OAuth2PasswordBearer= Depends()):  # 类作为依赖的导入方式
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:   # 没找到用户，报错
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect username or password')
    user = UserInDB(**user_dict)    # 找到用户就实例化
    hashed_password = fake_hash_password(form_data.password)    # 对表单密码加密
    if not hashed_password == user.hashed_password: # 对比加密后的密码和数据库密码是否相同
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect username or password')
    return {'access_token': user.username, 'token_type': 'bearer'}


from fastapi import HTTPException,status

# (用户登录成功后) 获取当前用户
async def get_current_user(token:str=Depends(oauth2_schema)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
        detail='Invalid authentication credentials',
        headers={'WWW-Authenticate': 'Bearer'}) # header加不加不影响，但这是规范
    return user


# (用户登录成功后) 获取当前活跃用户，disabled区分
async def get_current_active_user(current_user:User=Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Inactive user')
    return current_user



@app06.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user




''' ************** 3. OAuth2 with Password (and hashing), Bearer with JWT tokens 开发基于JSON Web Tokens的认证 ************** '''

"""
JWT过程如下：
1. 客户端发送用户名和密码到服务器。
2. 服务器验证用户名和密码。
3. 如果验证成功，服务器创建一个包含用户信息的JWT（JSON Web Token）。
4. 服务器将JWT返回给客户端。
5. 客户端在后续请求中包含JWT。
6. 服务器验证JWT的有效性。
7. 如果JWT有效，服务器处理请求；否则，返回错误。
"""



fake_users_db.update({
    "john snow": {
        "username": "john snow",
        "full_name": "John Snow",
        "email": "johnsnow@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
})

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # 生成密钥(Linux) openssl rand -hex 32
ALGORITHM = "HS256"  # 算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 访问令牌过期分钟


class Token(BaseModel):
    """返回给用户的Token"""
    access_token: str
    token_type: str

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

# bcrypt是加密算法，
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')   # 用于对密码加密
oauth2_schema = OAuth2PasswordBearer(tokenUrl='/chapter06/jwt/token')   # 请求Token的URL地址 http://127.0.0.1:8000/chapter06/jwt/token


def verify_password(plain_password: str, hashed_password: str):
    """校验密码是否正确"""
    return pwd_context.verify(plain_password, hashed_password)  # 第一个参数是明文密码，第二个参数是hash后的密码，返回True/False


# 获取当前用户
def jwt_get_user(db, username:str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None


# 对用户进行校验
def jwt_authenticate_user(db, username:str, password:str):
    user = jwt_get_user(db, username)
    if not user:    # 如果没有用户
        return False
    if not verify_password(password, user.hashed_password): # 如果密码错误
        return False
    return user


# 创建访问token（如果能找到用户且用户密码正确，就给用户创建访问token）
def create_access_token(data:dict, expires_delta:Optional[timedelta]=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp': expire})   # 更新token过期时间
    # 对token进行编码
    encoded_jwt = jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 写登录接口
@app06.post('/jwt/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm= Depends()):
    # 校验用户是否存在，密码是否正确
    user = jwt_authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Incorrect username or password', 
            headers={'WWW-Authenticate': 'Bearer'}
        )
    # 获取token的过期时间
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # 校验通过，创建访问token
    access_token = create_access_token(data={'sub': user.username}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'token_type': 'bearer'}


# 获取当前用户
async def jwt_get_current_user(token:str=Depends(oauth2_schema)):
    # 先定义错误，方便后面复用
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail='Could not validate credentials', 
        headers={'WWW-Authenticate': 'Bearer'}
    )

    try:
        # 编码时用什么key和算法，解码时也用什么key和算法，要保持一致
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get(key='sub')
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = jwt_get_user(fake_users_db, username)
    if not user:
        raise credentials_exception
    return user


# 获取当前活跃用户
async def jwt_get_current_active_user(current_user:User=Depends(jwt_get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Inactive user')
    return current_user



# 实现获取当前活跃用户的接口
@app06.get("/jwt/users/me", response_model=User)
async def jwt_read_users_me(current_user: User = Depends(jwt_get_current_active_user)):
    return current_user