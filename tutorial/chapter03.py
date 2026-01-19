from fastapi import APIRouter
from enum import Enum

app03 = APIRouter()


''' ************** 1. 路径参数和数字验证 ************** '''

# 这里没有传入路径参数
@app03.get('/path/parameters')
def path_params01():
    return {'message': 'This is a message'}

# 这里传入了路径参数
@app03.get('/path/{parameters}')
def path_params02(parameters: str): # 在函数里调用路径参数，参数名必须和路径参数名一致
    return {'message': parameters}

''' ！！ 函数的顺序就是路由的顺序 ！！ '''



''' 枚举类型参数 '''

# 枚举类型
class CityName(str, Enum):
    beijing = 'beijing china'
    shanghai = 'shanghai china'
    guangzhou = 'guangzhou china'

@app03.get('/enum/{city}')  # 枚举类型参数
async def get_city(city: CityName):
    if city == CityName.shanghai:
        return {'city_name': city, 'confirmed':1492, 'deaths':7}
    if city == CityName.beijing:
        return {'city_name': city, 'confirmed':971, 'deaths':9}
    return {'city_name': city, 'latest':'unknown'}


''' 通过路径参数传递文件路径 '''
@app03.get('/file/{file_path:path}')    # 通过路径参数传递文件路径，:path表示路径参数可以包含斜杠
async def get_file(file_path: str):
    return f"你请求的文件路径是：{file_path}"


''' 长度的使用 '''

from fastapi.params import Path     # Path，用于校验路径参数是否合规

@app03.get("/path_validate/{num}")
def path_params_validate(
    num:int = Path(..., title="路径参数", description="路径参数非空(...代表非空)，值大于等于1且小于等于100", ge=1, le=100)
):
    return {'message': num}





''' ************** 2. 查询参数和字符串验证 ************** '''

from typing import Optional


# 通常Web开发都会有分页的功能，分页通常会有两个参数：page和limit
# page表示当前页码，limit表示每页显示的数量
@app03.get('/query')    # 没有在路径中，所以page和limit是查询参数
def page_limit(page:int = 1, limit:Optional[int] = None):   # 给了默认值就是选填的参数，不给就是必填
    if limit:
        return {'page': page, 'limit': limit}
    return {'page': page}

# 有时路径中传递过来的值，可以直接转换为True/False(布尔类型)
# 传递值为：'true' 'TRUE' 'on' 'yes' 1 时，param为True
# 传递值为其他时，param可能是False也可能报错
@app03.get('/query/bool/conversion')
def type_conversion(param:bool = False):
    return {'param': param}



from fastapi.params import Query    # 对查询参数验证用Query，其它校验方法看Query类的源码

@app03.get('/query/validations')
def query_params_validate(
    value: str = Query(..., min_length=1, max_length=100, pattern="^[a-zA-Z0-9_]+$"), # 查询参数value，非空，长度在1-100之间，只能包含字母、数字和下划线
    values: list[str] = Query(default=['v1','v2'], alias='alias_name')  # 多个查询参数的列表，alias_name是查询参数的别名
):
    return {'value': value, 'values': values}


''' ************** 3. 请求体和字段 ************** '''
# “字段”指的是pydantic的Field类，可以用来定义请求体的数据格式和类型

from pydantic import BaseModel, Field

class CityInfo(BaseModel):
    name: str = Field(..., title="城市名称", description="城市名称非空", example="beijing") # example是示例值（不会被验证），给前端开发看的
    country: str
    country_code: str = None    # 给个默认值
    country_population:int = Field(default=800, ge=800, title="国家人口", description="必须大于等于800")    # 人口数量添加一个校验
    
    # 写一个CityInfo数据的示例，示例数据帮助前端开发人员理解 API 期望的数据结构
    # pydantic V2 使用 model_config 字典
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Shanghai",
                "country": "China",
                "country_code": "CN",
                "country_population": 1400000000,
            }
        }
    }

# 定义一个POST路由，用于接收CityInfo类型的请求体
@app03.post('/request_body/city')
def post_city_info(city: CityInfo):
    print(city.name, city.country, city.country_code, city.country_population)
    return city.model_dump()    # 将CityInfo对象转换为字典



''' ************** 4. Request Body + Path parameters + Query parameters 多参数混合 ************** '''

@app03.put('/request_body/city/{name}')
def mix_city_info(
    name: str,  # 路径参数
    city01: CityInfo,   # 请求体，可以是多个
    city02: CityInfo,   # 请求体
    confirmed = Query(ge=0, title="确认病例数", description="确认病例数必须大于等于0", default=0),  # 查询参数
    death = Query(ge=0, title="死亡病例数", description="死亡病例数必须大于等于0", default=0)   # 查询参数
):
    if name == "Shanghai":
        return {"Shanghai": {"confirmed": confirmed, "deaths": death}}
    return city01.model_dump() , city02.model_dump()


''' ************** 5. Request Body - Nested Models 数据格式嵌套的请求体 ************** '''
from datetime import date
from typing import List

# 定义一个嵌套的请求体格式
class Data(BaseModel):
    city: List[CityInfo] = None  # 这里是定义数据格式嵌套的请求体
    date: date  # 额外的数据类型，还有 uuid datetime bytes frozenset等，参考：https://fastapi.tiangolo.com/tutorial/extra-data-types/
    confirmed:int = Field(ge=0, title="确认病例数", description="确认病例数必须大于等于0", default=0)
    deaths:int = Field(ge=0, title="死亡病例数", description="死亡病例数必须大于等于0", default=0)
    recovered:int = Field(ge=0, title="恢复病例数", description="恢复病例数必须大于等于0", default=0)


@app03.put('/request_body/nested')
def post_data(data: Data):
    return data.model_dump()



''' ************** 6. Cookie 和 Header 参数 ************** '''

from fastapi.params import Cookie, Header

@app03.get('/cookie')   # 效果只能用Postman测试
def cookie(cookie_id:Optional[str]=Cookie(None)):   # 定义Cookie参数需要使用的Cookie类
    return {'cookie_id': cookie_id}

@app03.get('/header')
def header(user_agent: Optional[str] = Header(None, convert_underscores=True), x_token:List[str] = Header(None)): 
    """
    有些HTTP代理和服务器是不允许在请求头中带有下划线的，所以Header提供convert_underscores属性让设置
    :param user_agent: convert_underscores=True 会把 user_agent 变成 user-agent
    :param x_token: x_token是包含多个值的列表
    :return:
    """
    return {'User_Agent': user_agent, 'X_token': x_token}