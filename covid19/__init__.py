'''

目录结构：
covid19/
    __init__.py 
    static              存放静态文件
    template            前端代码
    models.py           模型类（对应数据库中的数据表）
    database.py         数据库配置
    schemas.py           响应体数据格式规范 （pydantic对应的模型类）
    crud.py             数据库操作
    main.py             应用入口

'''



from .main import application