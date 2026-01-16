### ORM

ORM是 Object-Relational Mapping （对象关系映射）的缩写，是一种将面向对象编程与关系型数据库连接起来的技术。
ORM的本质是 映射关系 ：
- 数据库的 表（Table） ↔ 编程语言的 类（Class）
- 表的 字段（Column） ↔ 类的 属性（Attribute）
- 表的 记录（Record） ↔ 类的 实例（Instance）
- SQL 查询操作 ↔ 类的 方法调用

常见的ORM框架

- Python：SQLAlchemy、Django ORM、Peewee
- Java：Hibernate、MyBatis



### WSGI（Web Server Gateway Interface）
WSGI是Python的标准Web服务器网关接口，定义了Web服务器与Python Web应用程序之间的通信规则。

核心特点 ：

- 同步处理 ：一次只能处理一个请求，请求处理完成后才能处理下一个
- 单协议支持 ：主要支持HTTP协议
- 简单模型 ：基于函数调用的简单模型
- 阻塞式IO ：每个请求会阻塞服务器直到完成

工作流程：客户端 → Web服务器（如Nginx、Apache）→ WSGI服务器 → WSGI应用（如Flask）→ 返回响应

代表框架：Flask、Django（Django 3.0之前）、Bottle、Pyramid

应用场景：适合简单的Web应用，开发成本低，生态成熟（如传统网站、管理后台）


### ASGI（Asynchronous Server Gateway Interface）
定义 ：ASGI是WSGI的异步后继者，专为异步Web应用设计，支持并发处理多个请求。

核心特点 ：

- 异步处理 ：支持并发处理多个请求，无需等待前一个请求完成
- 多协议支持 ：支持HTTP/1.1、HTTP/2和WebSocket等双向通信协议
- 事件驱动 ：基于事件循环的非阻塞IO模型
- 高性能 ：特别适合IO密集型应用和实时通信场景

工作流程 ：客户端 → Web服务器 → ASGI服务器 → ASGI应用（如FastAPI）→ 返回响应

代表框架 ：FastAPI、Starlette、Django 3.0+（支持ASGI）、Sanic、Tornado

应用场景：适合需要高性能、实时通信的应用（如API服务、聊天应用、实时数据推送、WebSocket服务）


### HTTP请求方法
HTTP 请求方法定义了客户端和服务器之间的通信方式。

根据 HTTP 标准，HTTP 请求可以使用多种请求方法。

以下是常见的 HTTP 请求方法列表：

|序号|方法|描述|
|--|--|--|
|1|GET|从服务器获取资源。用于请求数据而不对数据进行更改。例如，从服务器获取网页、图片等。|
|2|POST|向服务器发送数据以创建新资源。常用于提交表单数据或上传文件。发送的数据包含在请求体中。|
|3|PUT|向服务器发送数据以更新现有资源。如果资源不存在，则创建新的资源。与 POST 不同，PUT 通常是幂等的，即多次执行相同的 PUT 请求不会产生不同的结果。|
|4|DELETE|从服务器删除指定的资源。请求中包含要删除的资源标识符。|
|5|PATCH|对资源进行部分修改。与 PUT 类似，但 PATCH 只更改部分数据而不是替换整个资源。|
|6|HEAD|类似于 GET，但服务器只返回响应的头部，不返回实际数据。用于检查资源的元数据（例如，检查资源是否存在，查看响应的头部信息）。|
7|OPTIONS|返回服务器支持的 HTTP 方法。用于检查服务器支持哪些请求方法，通常用于跨域资源共享（CORS）的预检请求。|
|8|TRACE|回显服务器收到的请求，主要用于诊断。客户端可以查看请求在服务器中的处理路径。|
|9|CONNECT|建立一个到服务器的隧道，通常用于 HTTPS 连接。客户端可以通过该隧道发送加密的数据。|

