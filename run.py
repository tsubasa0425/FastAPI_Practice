

from fastapi import FastAPI
import uvicorn
from tutorial import app03, app04, app05, app06, app07, app08  # 注意，必须在tutorial\__init__.py中导入


app = FastAPI()

'''
该文件对应的地址就是 /
covid-19文件夹对应的地址就是 /covid-19
tutorial文件夹对应的地址就是 /tutorial

tutorial文件夹中，每个文件可以看作一个应用，app负责整合这些应用
'''

app.include_router(app03, prefix='/chapter03', tags=['第三章 请求参数和验证'])  # 将app03加入app，前缀为/chapter03，tags（标题）为chapter03
# app.include_router(app04, prefix='/chapter04', tags=['第四章 响应处理和FastAPI配置'])
# app.include_router(app05, prefix='/chapter05', tags=['第五章 FastAPI的依赖注入系统'])
# app.include_router(app06, prefix='/chapter06', tags=['chapter06'])
# app.include_router(app07, prefix='/chapter07', tags=['chapter07'])
# app.include_router(app08, prefix='/chapter08', tags=['chapter08'])



if __name__ == '__main__':
    # 等同于在终端输入 uvicorn hello_world:app --reload
    # 使用字符串导入格式以支持reload功能
    uvicorn.run("run:app", host='127.0.0.1', port=8000, reload=True)  # 自动更新


