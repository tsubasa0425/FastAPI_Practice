FastAPI入门课程：https://github.com/liaogx/fastapi-tutorial

`covid-19`：课程最终形成的项目

`run.py`：covid-19项目的运行文件

`tutorial`：课程代码


### 学习顺序

##### 0 `pydantic_tutorial.py`

Pydantic教程，基本模型及常用方法，递归模型，字段类型，校验，模型类配置


##### 1 `hello_world.py`

运行一个简单的 FastAPI 程序，实现返回 "hello world" 的接口；进一步，继承 Pydantic 的 BaseModel 规范请求体数据格式和类型，通过查询参数和请求体传递城市、所在国家、是否有感染病例的信息，讲解 FastAPI 框架的基本开发方法，同步和异步函数的编写、装饰器、URL 路由、HTTP 方法