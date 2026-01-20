from fastapi import APIRouter

app04 = APIRouter()

''' ************** 1. Response Model 响应模型 ************** '''

# 后端向前端返回数据时，通常需要定义一个响应模型，用于指定返回数据的结构和类型。
# 假设一个场景：用户在前端给后端传递一些用户信息（用户名，密码等），
# 后端在给前端返回的时候唯一要注意的字段就是密码（不能是明文，会去掉，其余信息保留）

from pydantic import BaseModel, EmailStr    # EmailStr会自动校验邮箱格式
from typing import Optional, Union    # Optional表示可选字段，Union表示可以是多个类型中的任意一个

# 定义请求体（客户端 → 服务器）
class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr # 用 EmailStr 需要 pip install pydantic[email]
    mobile: str = '10086'
    address: str = None
    full_name: Optional[str] = None


# 定义响应体（服务器 → 客户端）
class UserOut(BaseModel):
    username: str
    email: EmailStr
    mobile: str = '10086'
    address: str
    full_name: Optional[str] = None


users = {   # 定义一些请求体的信息
    "user01": {"username": "user01", "password": "123123", "email": "user01@example.com"},
    "user02": {"username": "user02", "password": "123456", "email": "user02@example.com", "mobile": "110"}
}


@app04.post("/response_model/", response_model=UserOut, response_model_exclude_unset=True)
async def response_model(user: UserIn):
    """response_model_exclude_unset=True表示默认值不包含在响应中，仅包含实际给的值，如果实际给的值与默认值相同也会包含在响应中"""
    print(user.password)    # password不会被返回
    return user["user01"]


'''
Union[UserIn, UserOut] ：优先匹配 UserIn ，返回包含 password 的完整数据
Union[UserOut, UserIn] ：先尝试匹配 UserOut 失败（缺少password），再匹配 UserIn 成功，同样返回包含 password 的完整数据
'''
@app04.post(
    "/reponse_model/attributes",
    # response_model=UserOut,
    response_model=Union[UserIn, UserOut]
    # response_model_include=["username", "email", "mobile", "address", "full_name"]    # 包含哪些字段
    # response_model_exclude=["password"]    # 排除哪些字段
)
async def response_model_attributes(user: UserIn):
    return user # 此时会把请求体和响应体的所有字段都返回，包括password



''' ************** 2. Response Status Code 响应状态码 ************** '''

from fastapi import status

@app04.post("/status_code", status_code=200)
async def status_code():
    return {"status_code": 200, "message": "Success"}

@app04.post("/status_code", status_code=status.HTTP_200_OK)
async def status_attribute():
    print(type(status.HTTP_200_OK))
    return {"status_code": status.HTTP_200_OK, "message": "Success"}


''' ************** 3. Form Data 表单数据处理 ************** '''
from fastapi import Form

@app04.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):  # 定义表单参数, ...代表必填
    """用Form类需要pip install python-multipart; Form类的元数据和校验方法类似Body/Query/Path/Cookie"""
    return {"username": username}


''' ************** 4. Request Files 单文件、多文件上传及参数详解 ************** '''

from fastapi import File, UploadFile
from typing import List

# 上传单个文件
@app04.post("/file")
async def file_(file: bytes = File(...)):   # 如果要上传多个文件 files: List[bytes] = File(...)
    """使用File类，文件内容会以bytes的形式读入内存，适合上传小文件，如果是大文件，内存会爆掉"""
    return {"file_size": len(file)}

# 上传多个文件
@app04.post("/upload_files")
async def uploadfile_(files: List[UploadFile] = File(...)):     # 如果要上传单个文件 file: UploadFile = File(...)
    """
    使用UploadFile类的优势:
    1.文件存储在内存中，使用的内存达到阈值后，将被保存在磁盘中
    2.适合于图片、视频大文件
    3.可以获取上传的文件的元数据，如文件名，创建时间等
    4.有文件对象的异步接口
    5.上传的文件是Python文件对象，可以使用write(), read(), seek(), close()操作
    """
    for file in files:
        contents = await file.read()    # 因为函数定义了async，所以这里需要await
        print(contents)
    return {"filename": files[0].filename, "content_type": files[0].content_type}



''' ************** 5. 【见run.py】FastAPI项目的静态文件配置 ************** '''


''' ************** 6. Path Operation Configuration 路径操作配置 ************** '''

@app04.post(
    "/path_operation_configuration",
    response_model=UserOut,
    # response_model_exclude_unset=True,
    description="这是一个路径操作配置的示例",
    tags=["路径操作配置"],   # 可以在API交互文档中分组显示
    response_description="返回用户信息",    
    # deprecated=True,     # 表示该路径操作已被弃用，但在API交互文档中仍可测试
    status_code=status.HTTP_201_CREATED
)
async def path_operation_configuration(user: UserIn):
    return user.model_dump()


''' ************** 7. 【见run.py】FastAPI 应用的常见配置项 ************** '''



''' ************** 8. Handling Errors 错误处理 ************** '''
from fastapi.exceptions import HTTPException

@app04.get('/http_exception')
async def http_exception(city:str):
    if city!="Beijing":
        raise HTTPException(status_code=404, detail="City not found", headers={"X-Error": "City not found"})
    return {"city": city}


# 测试重写的HTTPException异常处理器
@app04.get('/http_exception/{city_id}')
async def override_http_exception(city_id:int):
    if city_id == 1:
        raise HTTPException(status_code=418, detail="Nope! I don't have that city", headers={"X-Error": "I don't have that city"})
    return {"city_id": city_id}
