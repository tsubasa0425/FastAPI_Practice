
from pydantic import BaseModel
from datetime import datetime
from datetime import date as date_



'''
class City(Base):
    __tablename__ = 'city'  # 数据表的表名

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    province = Column(String(100), unique=True, nullable=False, comment='省/直辖市')
    country = Column(String(100), nullable=False, comment='国家')
    country_code = Column(String(100), nullable=False, comment='国家代码')
    country_population = Column(BigInteger, nullable=False, comment='国家人口')
    data = relationship('Data', back_populates='city')  # 'Data'是关联的类名；back_populates来指定反向访问的属性名称

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    __mapper_args__ = {"order_by": country_code}  # 默认是正序，倒序加上.desc()方法

    def __repr__(self):
        return f'{self.country}_{self.province}'
'''

class CreateCity(BaseModel):
    """字段参考models.py里的City类"""
    id: int
    created_at:datetime
    updated_at:datetime

    model_config = {
        "from_attributes": True,
    }


class ReadCity(CreateCity):
    province: str
    country: str
    country_code: str
    country_population: int = 0


'''
class Data(Base):
    __tablename__ = 'data'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    city_id = Column(Integer, ForeignKey('city.id'), comment='所属省/直辖市')  # ForeignKey里的字符串格式不是类名.属性名，而是表名.字段名
    date = Column(Date, nullable=False, comment='数据日期')
    confirmed = Column(BigInteger, default=0, nullable=False, comment='确诊数量')
    deaths = Column(BigInteger, default=0, nullable=False, comment='死亡数量')
    recovered = Column(BigInteger, default=0, nullable=False, comment='痊愈数量')
    city = relationship('City', back_populates='data')  # 'City'是关联的类名；back_populates来指定反向访问的属性名称

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    __mapper_args__ = {"order_by": date.desc()}  # 按日期降序排列

    def __repr__(self):
        return f'{repr(self.date)}：确诊{self.confirmed}例'

'''


class CreateData(BaseModel):
    """字段参考models.py里的Data类"""
    id: int
    city_id:int
    created_at:datetime
    updated_at:datetime

    model_config = {
        "from_attributes": True,
    }



class ReadData(CreateData):
    date: date_
    confirmed: int = 0
    deaths: int = 0
    recovered: int = 0

    
