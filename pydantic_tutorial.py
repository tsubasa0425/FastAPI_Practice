#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "__Jack__"

from datetime import datetime, date
from pathlib import Path
from typing import List
from typing import Optional

from pydantic import BaseModel, ValidationError
from pydantic import constr
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base

"""
Data validation and settings management using python type annotations.
使用Python的类型注解来进行数据校验和settings管理

pydantic enforces type hints at runtime, and provides user friendly errors when data is invalid.
Pydantic可以在代码运行时提供类型提示，数据校验失败时提供友好的错误提示

Define how data should be in pure, canonical python; validate it with pydantic.
定义数据应该如何在纯规范的Python代码中保存，并用Pydantic验证它
"""

print("\033[31m1. --- Pydantic的基本用法。 ---\033[0m")


class User(BaseModel):
    id: int  # 没设定默认值，就是必填字段
    name: str = "John Snow"  # 有默认值，选填字段
    signup_ts: Optional[datetime] = None    # 可以用Optional设定选填字段
    friends: List[int] = []  # 列表中元素是int类型或者可以直接转换成int类型


external_data = {
    "id": "123",    # 如果给id赋值为字符串，会自动转换为int类型，但如果赋值的字符串不能转换为int类型，会报错
    "signup_ts": "2020-12-22 12:22",    # 要填入可以转化为datetime类型的数据，否则报错
    "friends": [1, 2, "3"],  # "3"是可以int("3")的
}
user = User(**external_data)
print(user.id, user.friends)  # 实例化后调用属性
print(repr(user.signup_ts))
# print(user.dict())  # 老写法，pydantic V1.x
print(user.model_dump())  # 新写法，pydantic V2.x

print("\033[31m2. --- 校验失败处理 ---\033[0m")
try:
    User(id=1, signup_ts=datetime.today(), friends=[1, 2, "not number"])
except ValidationError as e:
    print(e.json())

print("\033[31m3. --- 模型类的的属性和方法 ---\033[0m")
# 老写法，pydantic V1.x
# print(user.dict())
# print(user.json())
# print(user.copy())  # 这里是浅拷贝
# print(User.parse_obj(external_data))
# print(User.parse_raw('{"id": "123", "signup_ts": "2020-12-22 12:22", "friends": [1, 2, "3"]}'))

# 新写法，pydantic V2.x
print(user.model_dump())
print(user.model_dump_json())
print(user.model_copy())  # 这里是浅拷贝
print(User.model_validate(external_data))
print(User.model_validate_json('{"id": "123", "signup_ts": "2020-12-22 12:22", "friends": [1, 2, "3"]}'))


path = Path('pydantic_tutorial.json')
path.write_text('{"id": "123", "signup_ts": "2020-12-22 12:22", "friends": [1, 2, "3"]}')
# print(User.parse_file(path))  # 老写法，pydantic V1.x
print(User.model_validate_json(path.read_text())) # 新写法，pydantic V2.x
# - Pydantic V2中移除了V1版本的 parse_file 和 parse_raw 方法
# - 这些功能统一由 model_validate_json 方法替代
# - 对于文件操作，需要先手动读取文件内容，然后再进行验证


# print(user.schema())
# print(user.schema_json())
print(user.model_json_schema())  # Pydantic V2中schema()和schema_json()合并为一个方法

user_data = {"id": "error", "signup_ts": "2020-12-22 12 22", "friends": [1, 2, 3]}  # id是字符串 是错误的
# print(User.construct(**user_data))  # 不检验数据直接创建模型类，不建议在construct方法中传入未经验证的数据
print(User.model_construct(**user_data))  # 新写法，pydantic V2.x


# print(User.__fields__.keys())  # 定义模型类的时候，所有字段都注明类型，字段顺序就不会乱
print(User.model_fields.keys())  # Pydantic V2中__fields__替换为model_fields

print("\033[31m4. --- 递归模型 ---\033[0m")


class Sound(BaseModel):
    sound: str


class Dog(BaseModel):
    birthday: date
    weight: float = Optional[None]
    sound: List[Sound]  # 不同的狗有不同的叫声。递归模型（Recursive Models）就是指一个嵌套一个


dogs = Dog(birthday=date.today(), weight=6.66, sound=[{"sound": "wang wang ~"}, {"sound": "ying ying ~"}])
# print(dogs.dict())
print(dogs.model_dump())

print("\033[31m5. --- ORM模型：从类实例创建符合ORM对象的模型  ---\033[0m")

Base = declarative_base()


class CompanyOrm(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True, nullable=False)  # 数字，主键，不能为空
    public_key = Column(String(20), index=True, nullable=False, unique=True)    # 字符串（20个字符），索引，不能为空，唯一
    name = Column(String(63), unique=True)    # 字符串（63个字符），唯一
    domains = Column(ARRAY(String(255)))     # 数组，每个元素是字符串（255个字符）


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


co_orm = CompanyOrm(
    id=123,
    public_key='foobar',
    name='Testing',
    domains=['example.com', 'foobar.com'],
)

# print(CompanyModel.from_orm(co_orm))
print(CompanyModel.model_validate(co_orm, from_attributes=True))  # Pydantic V2中from_orm替换为model_validate，并使用from_attributes参数

print("\033[31m6. --- Pydantic支撑的字段类型  ---\033[0m")  # 官方文档：https://pydantic-docs.helpmanual.io/usage/types/