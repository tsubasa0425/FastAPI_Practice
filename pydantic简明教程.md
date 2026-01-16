# Pydantic简明教程

使用Python的类型注解来进行数据校验和settings管理
> Data validation and settings management using python type annotations.

Pydantic可以在代码运行时提供类型提示，数据校验失败时提供友好的错误提示
> pydantic enforces type hints at runtime, and provides user friendly errors when data is invalid.

定义数据应该如何在纯规范的Python代码中保存，并用Pydantic验证它
> Define how data should be in pure, canonical python; validate it with pydantic.


代码在pydantic_tutorial.py文件中


### 1. Pydantic的基本使用

定义一个User类，集成BaseModel


```python

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class User(BaseModel):
    id: int  # 没设定默认值，就是必填字段
    name: str = "John Snow"  # 有默认值，选填字段
    signup_ts: Optional[datetime] = None    # 可以用Optional设定选填字段
    friends: List[int] = []  # 列表中元素是int类型或者可以直接转换成int类型

```

定义要传递给User类的数据

```python

external_data = {
    "id": "123",    # 如果给id赋值为字符串，会自动转换为int类型，但如果赋值的字符串不能转换为int类型，会报错
    "signup_ts": "2020-12-22 12:22",    # 要填入可以转化为datetime类型的数据，否则报错
    "friends": [1, 2, "3"],  # "3"是可以int("3")的
}

```

怎么把数据传递给User呢？

可以使用数据解包

```python

user = User(**external_data)
print(user.id, user.friends)  # 实例化后调用属性
print(repr(user.signup_ts))
# print(user.dict())  # 老写法，pydantic V1.x
print(user.model_dump())  # 新写法，pydantic V2.x

```

对应的输出是：

```terminal
123 [1, 2, 3]
datetime.datetime(2020, 12, 22, 12, 22)
{'id': 123, 'name': 'John Snow', 'signup_ts': datetime.datetime(2020, 12, 22, 12, 22), 'friends': [1, 2, 3]}
```

如果给id赋值为字符串"1a23"，会报错

```terminal
(venv) (base) D:\python练习\FastAPI练习>python pydantic_tutorial.py
1. --- Pydantic的基本用法。Pycharm可以安装Pydantic插件 ---
Traceback (most recent call last):
  File "D:\python练习\FastAPI练习\pydantic_tutorial.py", line 42, in <module>
    user = User(**external_data)
           ^^^^^^^^^^^^^^^^^^^^^
  File "D:\python练习\FastAPI练习\venv\Lib\site-packages\pydantic\main.py", line 250, in __init__      
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for User
id
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='1a23', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/int_parsing
```

### 2. 校验失败处理

当校验失败时，Pydantic会抛出ValidationError异常，可以捕获这个异常，然后处理它。


```python

from pydantic import ValidationError

try:
    User(id=1, signup_ts=datetime.today(), friends=[1, 2, "not number"])
except ValidationError as e:
    print(e.json()) # 打印校验失败的详细信息（可以被json格式化）
```

对应的输出是：
```json
[
    {"type":"int_parsing",  // 错误的类型
    "loc":["friends",2],    // 错误的位置
    "msg":"Input should be a valid integer, unable to parse string as an integer",  // 错误的原因
    "input":"not number",
    "url":"https://errors.pydantic.dev/2.12/v/int_parsing"}
] 

```


### 3. BaseModel的属性和方法

pydantic V1.x 和 V2.x 中的BaseModel有一些共同属性和方法，但是它们的命名和使用方式不同。

```python

# 老写法，pydantic V1.x
# print(user.dict())
# print(user.json())
# print(user.copy())  # 这里是浅拷贝
# print(User.parse_obj(external_data))
# print(User.parse_raw('{"id": "123", "signup_ts": "2020-12-22 12:22", "friends": [1, 2, "3"]}'))

# 新写法，pydantic V2.x
print(user.model_dump())    # 直接把实例数据转换为字典
print(user.model_dump_json())
print(user.model_copy())  # 这里是浅拷贝

print(User.model_validate(external_data))   # 模型类的解析数据方法，把数据转换为模型实例（类似于数据解包 **external_data）
print(User.model_validate_json('{"id": "123", "signup_ts": "2020-12-22 12:22", "friends": [1, 2, "3"]}'))   # 模型类的解析json数据方法，把json数据转换为模型实例

```

同样，模型类也可以解析文件

```python

from pathlib import Path

path = Path('pydantic_tutorial.json')   # 在当前路径下，创建一个数据文件
path.write_text('{"id": "123", "signup_ts": "2020-12-22 12:22", "friends": [1, 2, "3"]}')   # 在文件中写入内容

# print(User.parse_file(path))  # 老写法，pydantic V1.x
print(User.model_validate_json(path.read_text())) # 新写法，pydantic V2.x
# - Pydantic V2中移除了V1版本的 parse_file 和 parse_raw 方法
# - 这些功能统一由 model_validate_json 方法替代
# - 对于文件操作，需要先手动读取文件内容，然后再进行验证

```
> - Pydantic V2中移除了V1版本的 parse_file 和 parse_raw 方法
> - 这些功能统一由 model_validate_json 方法替代
> - 对于文件操作，需要先手动读取文件内容，然后再进行验证


也有一些方法可以获取模型类定义的数据格式


```python

# 老写法，pydantic V1.x
# print(user.schema())
# print(user.schema_json())

print(user.model_json_schema())  # Pydantic V2中schema()和schema_json()合并为一个方法

```

对应的输出是：

```json
{
    "properties": {
        "id": {"title": "Id", "type": "integer"}, 
        "name": {"default": "John Snow", "title": "Name", "type": "string"}, 
        "signup_ts": {  
            "anyOf": [{"format": "date-time", "type": "string"}, {"type": "null"}], 
            "default": None, 
            "title": "Signup Ts"}, 
        "friends": {
            "default": [], 
            "items": {"type": "integer"}, 
            "title": "Friends", 
            "type": "array"}}, 
    "required": ["id"], 
    "title": "User", 
    "type": "object"
}
```


还有一个解析数据的方法，但与 model_validate 方法不同的是，它不会进行校验，也不会报错

```python

user_data = {"id": "error", "signup_ts": "2020-12-22 12 22", "friends": [1, 2, 3]}  # id是字符串 是错误的

# 不检验数据直接创建模型类，!!不建议在model_construct方法中传入未经验证的数据!!
# print(User.construct(**user_data)) # 老写法
print(User.model_construct(**user_data))  # 新写法，pydantic V2.x

```

对应的输出没有报错：
```terminal
id='error' name='John Snow' signup_ts='2020-12-22 12 22' friends=[1, 2, 3]
```


最后关于字段顺序的问题

定义模型类的时候，所有字段都注明类型，字段顺序就不会乱

```python
# print(User.__fields__.keys())  # 老写法
print(User.model_fields.keys())  # Pydantic V2中__fields__替换为model_fields
```
对应的输出是：

```terminal
dict_keys(['id', 'name', 'signup_ts', 'friends'])
```


### 4. 递归模型

就是在一个模型类中，调用另一个模型类定义数据的格式/规范

比如让 Dog 模型类调用 Sound 模型类定义数据的格式

```python

from datetime import date
from typing import List, Optional

class Sound(BaseModel):
    sound: str


class Dog(BaseModel):   # 注意不是继承Sound
    birthday: date
    weight: float = Optional[None]
    sound: List[Sound]  # 不同的狗有不同的叫声。递归模型（Recursive Models）就是指一个嵌套一个


# 实例化一个 Dog 类的对象，这个对象今天出生，重6.66kg，有两种叫声
dogs = Dog(birthday=date.today(), weight=6.66, sound=[{"sound": "wang wang ~"}, {"sound": "ying ying ~"}])
# print(dogs.dict())    # 老写法
print(dogs.model_dump())    # 新写法
```
> 注意，实例化dog时，sound字段是一个列表，每个元素都是一个Sound类的实例。`{"sound": "wang wang ~"}`这个键值对就直接给Sound类的sound字段赋值了。

对应的输出是：
```terminal
{'birthday': datetime.date(2023, 12, 22), 'weight': 6.66, 'sound': [{'sound': 'wang wang ~'}, {'sound': 'ying ying ~'}]}
```

### 5. ORM模型：从类实例创建符合ORM对象的模型

既然可以定义字段，还能嵌套，还有方法调用，那Pydantic就能和ORM模型类进行关联

> ORM是 Object-Relational Mapping （对象关系映射）的缩写，是一种将面向对象编程与关系型数据库连接起来的技术。


```python
# sqlalchemy时Python生态中常用的ORM框架
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
# from sqlalchemy.ext.declarative import declarative_base   # 老版本
from sqlalchemy.orm import declarative_base

# 创建两个模型类（就是两张表）
Base = declarative_base()

# 定义数据表要用的ORM模型类
class CompanyOrm(Base):
    __tablename__ = 'companies' # 数据表名
    id = Column(Integer, primary_key=True, nullable=False)  # 数字，主键，不能为空
    public_key = Column(String(20), index=True, nullable=False, unique=True)    # 字符串（20个字符），索引，不能为空，唯一
    name = Column(String(63), unique=True)    # 字符串（63个字符），唯一
    domains = Column(ARRAY(String(255)))     # 数组，每个元素是字符串（255个字符）

# 定义数据表要用的Pydantic模型类，和ORM模型类的字段对应
class CompanyModel(BaseModel):
    id: int
    public_key: constr(max_length=20)   # 字符串（20个字符），constr是用来限制字符串长度的
    name: constr(max_length=63)
    domains: List[constr(max_length=255)]

    # class Config:
        # orm_mode = True
    
    model_config = {    # 表示数据格式与ORM模型类对应
        "from_attributes": True  # Pydantic V2中使用model_config替代class Config
    }

```
**ORM模型类和Pydantic模型类的协作关系**

在现代Web应用（如FastAPI项目）中，常见的数据流是：

- 前端请求 → Pydantic模型验证输入 → 转换为ORM对象 → 数据库操作
- 数据库查询 → ORM对象 → 转换为Pydantic模型 → 返回给前端

> 代码中的 `model_config={"from_attributes": True}` 配置就是为了支持从ORM对象到Pydantic模型的自动转换。

**为什么要分离？**
- 关注点分离 ：数据库操作和API数据处理逻辑分开，代码更清晰
- 灵活性 ：可以根据前端需求调整API响应结构，而不影响数据库设计
- 安全性 ：可以控制哪些字段暴露给前端（避免敏感数据泄露）
- 性能 ：只返回前端需要的数据，减少网络传输


来试试效果：

```python

# 实例化一个ORM模型类的对象
co_orm = CompanyOrm(
    id=123,
    public_key='foobar',
    name='Testing',
    domains=['example.com', 'foobar.com'],
)

# 从ORM模型类的对象创建一个Pydantic模型类的对象
# print(CompanyModel.from_orm(co_orm))  # 老写法
print(CompanyModel.model_validate(co_orm, from_attributes=True))  # Pydantic V2中from_orm替换为model_validate，并使用from_attributes参数

```

对应的输出为：
```terminal
id=123 public_key='foobar' name='Testing' domains=['example.com', 'foobar.com']
```



### 6. Pydantic支撑的字段类型

见[官方文档](https://pydantic-docs.helpmanual.io/usage/types/)