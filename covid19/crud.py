from sqlalchemy.orm import Session
from covid19 import models, schemas


def get_city(db:Session, city_id:int):
    # 相当于SQL: SELECT * FROM city WHERE id = city_id
    return db.query(models.City).filter(models.City.id == city_id).first()


def get_city_by_name(db:Session, city_name:str):
    # 相当于SQL: SELECT * FROM city WHERE name = city_name
    return db.query(models.City).filter(models.City.name == city_name).first()

def get_cities(db:Session, skip:int=0, limit:int=10):
    # 相当于SQL: SELECT * FROM city LIMIT limit OFFSET skip
    return db.query(models.City).offset(skip).limit(limit).all()


def create_city(db:Session, city:schemas.CreateCity):
    # 相当于SQL: INSERT INTO city (name, province, country, country_code, country_population) VALUES (city.name, city.province, city.country, city.country_code, city.country_population)
    db_city = models.City(**city.model_dump())
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city


def get_data(db:Session, city:str=None, skip:int=0, limit:int=10):
    if city:    # 按照城市名字查询
        # 相当于SQL: SELECT * FROM data WHERE city.province = city
        return db.query(models.Data).filter(models.Data.city.has(province=city))   # 外键关联查询，这里不是像Django ORM那样Data.city.province
    # 没有城市名字就分页查询
    # 相当于SQL: SELECT * FROM data LIMIT limit OFFSET skip
    return db.query(models.Data).offset(skip).limit(limit).all()



def create_city_data(db:Session, data:schemas.CreateData, city_id:int):
    # 相当于SQL: INSERT INTO data (city_id, date, confirmed, deaths, recovered) VALUES (city_id, data.date, data.confirmed, data.deaths, data.recovered)
    db_data = models.Data(**data.model_dump(), city_id=city_id)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data