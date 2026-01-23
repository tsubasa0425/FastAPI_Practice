

from fastapi import FastAPI
import uvicorn
from tutorial import app03, app04, app05, app06, app07, app08  # 注意，必须在tutorial\__init__.py中导入
from covid19 import application



''' ************** Chapter04 7. FastAPI 应用的常见配置项 ************** '''

app = FastAPI(
    title='FastAPI Tutorial and Coronavirus Tracker API Docs',  # 应用标题，Swagger UI 页面顶部显示
    description='FastAPI教程 新冠病毒疫情跟踪器API接口文档，项目代码：https://github.com/liaogx/fastapi-tutorial',  # 应用描述，Swagger UI 页面顶部显示
    version='1.0.0',    # 应用版本，Swagger UI 页面顶部显示
    docs_url='/docs',    # 文档URL，默认是 /docs
    redoc_url='/redocs',    # ReDoc URL，默认是 /redocs
)

''' ************** *********************** ************** '''


'''
该文件对应的地址就是 /
covid-19文件夹对应的地址就是 /covid-19
tutorial文件夹对应的地址就是 /tutorial

tutorial文件夹中，每个文件可以看作一个应用，app负责整合这些应用
'''

app.include_router(app03, prefix='/chapter03', tags=['第三章 请求参数和验证'])  # 将app03加入app，前缀为/chapter03，tags（标题）为chapter03
app.include_router(app04, prefix='/chapter04', tags=['第四章 响应处理和FastAPI配置'])
app.include_router(app05, prefix='/chapter05', tags=['第五章 FastAPI的依赖注入系统'])
app.include_router(app06, prefix='/chapter06', tags=['第六章 安全、认证和授权'])
app.include_router(app07, prefix='/chapter07', tags=['第七章 FastAPI的数据库操作和多应用的目录结构设计'])
app.include_router(application, prefix='/covid19', tags=['新冠病毒疫情跟踪器API'])
app.include_router(app08, prefix='/chapter08', tags=['第八章 中间件、CORS、后台任务、测试用例'])



''' ************** Chapter04 5. FastAPI项目的静态文件配置 ************** '''

from fastapi.staticfiles import StaticFiles
# path是Http请求的路径，app是StaticFiles类的实例，directory是静态文件所在的目录，name是挂载的名称
app.mount(path='/static', app=StaticFiles(directory='covid19/static'), name='static')
# mount表示将某个目录下一个完全独立的应用挂载过来，这个不会在API交互文档中显示

''' ************** *********************** ************** '''



''' ************** Chapter04 8. Handling Errors 错误处理 ************** '''
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)  # 重写HTTPException异常处理器
async def http_exception_handler(request, exc):
    """
    :param request: 请求对象，这个参数不能省略
    :param exc: 异常对象
    :return: 响应对象, 不再是JSON格式, 而是文本格式
    """
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

@app.exception_handler(RequestValidationError)  # 重写请求验证异常处理器
async def validation_exception_handler(request, exc):
    """
    :param request: 请求对象，这个参数不能省略
    :param exc: 异常对象
    :return: 响应对象, 不再是JSON格式, 而是文本格式
    """
    return PlainTextResponse(str(exc), status_code=400)

''' ************** *********************** ************** '''




''' ************** Chapter08 1.Middleware 中间件 ************** '''
# 中间件：
# 中间件是在请求处理过程中，FastAPI 会在每个请求到达路由处理函数之前调用中间件函数。
# 中间件函数可以在请求处理过程中添加、修改或删除请求头、请求体、响应头、响应体等。
# 中间件函数可以用于实现日志记录、性能监控、认证授权、CORS（跨域资源共享）等功能。

import time
from fastapi.requests import Request

@app.middleware('http')
async def add_process_time_header(request:Request, call_next):  # call_next将接收request请求作为参数
    """
    中间件函数，用于添加处理时间头信息。

    :param request: 请求对象，包含请求信息。
    :param call_next: 下一个中间件函数或路由处理函数。
    :return: 响应对象，包含处理结果和头信息。
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers['X-Process-Time'] = str(process_time)  # 添加自定义的以“X-”开头的请求头
    return response


# ！！注意：带yield的依赖的退出部分的代码 和 后台任务 会在中间件之后运行！！

''' ************** *********************** ************** '''

''' ************** Chapter08 2.CORS (Cross-Origin Resource Sharing) 跨源资源共享 ************** '''


from fastapi.middleware.cors import CORSMiddleware

# 域的概念：协议+域名+端口

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://127.0.0.1',
        'http://127.0.0.1:8080',
    ],  # 允许的域
    allow_credentials=True,
    allow_methods=['*'],  # 允许所有方法
    allow_headers=['*'],  # 允许所有头信息
)


''' ************** *********************** ************** '''


if __name__ == '__main__':
    # 等同于在终端输入 uvicorn hello_world:app --reload
    # 使用字符串导入格式以支持reload功能
    uvicorn.run("run:app", host='127.0.0.1', port=8000, reload=True)  # 自动更新


