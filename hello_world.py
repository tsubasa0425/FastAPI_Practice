#!/usr/bin/python3
# -*- coding:utf-8 -*-

"""
运行一个简单的 FastAPI 程序，实现返回 "hello world" 的接口；
进一步，继承 Pydantic 的 BaseModel 规范请求体数据格式和类型，
通过查询参数和请求体传递城市、所在国家、是否有感染病例的信息，
讲解 FastAPI 框架的基本开发方法，同步和异步函数的编写、装饰器、URL 路由、HTTP 方法
"""


from fastapi import FastAPI
from pydantic import BaseModel

from typing import Optional

app = FastAPI() # 这里不一定是app，名字随意

class CityInfo(BaseModel):
    province: str
    country: str
    is_infected: Optional[bool] = None   # 可选字段，可以不填，默认值为 None
    # is_infected: bool   # 如果没有Optional，也没有默认值，那么这个字段就是必填的


@app.get("/")   # 将静态函数定义为fastapi的路由函数（api接口），就使用这个装饰器
def hello_world():
    '''
    @app.get 指定使用GET方法处理请求（类似的还有 @app.post , @app.put , @app.delete 等）
    ("/")  这里的"/"就是url地址, 浏览器访问这个地址, 就会调用hello_world函数
            如果想在url中传递参数,就可以在"/"后面添加参数, 例如: @app.get("/city/{city}")
    '''
    return {"message": "hello world"}   # 返回一个键值对



@app.get("/city/{city}")  # 这里的{city}就是url中传递的参数，url中没有查询参数也能成功调用result0，不会报错
def result0(city: str, query_string: Optional[str] = None):
    # 查询参数（Query Parameters）是URL中用于传递额外信息的部分，位于 ? 符号之后，使用 & 分隔多个参数。
    # 例如： http://localhost:8000/items?skip=0&limit=10， 这里的skip和limit就是查询参数，0和10是对应的值
    # 在FastAPI中，定义查询参数非常简单，只需在函数参数中添加非路径参数，这里的query_string是查询参数(类型定义为选填)
    return {"city": city, "query_string": query_string}

@app.get("/city/{city}")  # fastapi的匹配原则是，先匹配前面的，再匹配后面的。
# 比如输入 http://localhost:8000/city/Shanghai，会优先匹配到result0函数，而不是result函数
# 因为result0函数的查询参数是可选的，而result函数的查询参数是必填的
# 如果result在result0前面定义，那么输入 http://localhost:8000/city/Shanghai 时，会优先匹配到result函数，此时就会报错
def result(city: str, query_string: str):
    # 这里的query_string是查询参数(类型定义为必填)
    return {"city": city, "query_string": query_string}


# 启动命令： uvicorn hello_world:app --reload
# --reload  开启自动重载，当代码发生改变时，会自动重启服务器


@app.put("/city/{city}")  # 不同的方法，可以使用相同的路径，处理函数的命名也可以相同（也可以叫result），但在开发时尽量避免同名函数
def result_put(city: str, city_info: CityInfo): 
    # 在这里要使用前面定义好的CityInfo类，向/city{city} 路径传递城市信息
    # 可在fastapi提供的swagger文档中测试(localhost:8000/docs)，输入城市信息，点击Execute，即可看到返回结果
    return {"city": city, "country": city_info.country, "is_infected": city_info.is_infected}


# --------------------------------------------------


# 以上是同步方法的定义，异步方法的定义也很简单，在函数定义前加个async关键字即可
@app.get("/city/{city}/async")
async def result_async(city: str, query_string: Optional[str] = None):
    return {"city": city, "query_string": query_string}



# API文档
# 访问 http://localhost:8000/docs 即可查看swagger文档，可交互，测试接口
# 访问 http://localhost:8000/redoc 即可查看redoc文档，只能看