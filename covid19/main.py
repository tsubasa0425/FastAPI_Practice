"""        COVID-19 感染数据查询接口         """


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from covid19 import crud, schemas
from covid19.database import engine, Base, SessionLocal
from covid19.models import City, Data


application = APIRouter()


Base.metadata.create_all(bind=engine)

# 公用函数，获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


'''--------------- 和crud.py里的方法对应 ---------------'''


# 创建城市
@application.post('/create_city', response_model=schemas.ReadCity)
def create_city(city: schemas.CreateCity, db: Session = Depends(get_db)):
    db_city = crud.get_city_by_name(db, city.province)
    if db_city:
        raise HTTPException(status_code=400, detail='City already registered')
    return crud.create_city(db=db, city=city)



# 查询城市，根据名称
@application.get('/city/{city}', response_model=schemas.ReadCity)
def read_city_by_name(city: str, db: Session = Depends(get_db)):
    db_city = crud.get_city_by_name(db, city)
    if db_city is None:
        raise HTTPException(status_code=404, detail='City not found')
    return db_city

from typing import List

# 查询多个城市
@application.get('/cities', response_model=List[schemas.ReadCity])
def read_cities(skip:int=0, limit:int=10, db: Session = Depends(get_db)):
    cities = crud.get_cities(db, skip=skip, limit=limit)
    return cities


# 创建数据
@application.post('/create_data', response_model=schemas.ReadData)
def create_data_for_city(city:str, data: schemas.CreateData, db: Session = Depends(get_db)):
    db_city = crud.get_city_by_name(db, city)
    data = crud.create_data(db=db, data=data, city_id=db_city.id)
    return data


# 查询数据
@application.get('/get_data', response_model=List[schemas.ReadData])
def read_data_for_city(city:str=None, skip:int=0, limit:int=10, db: Session = Depends(get_db)):
    data = crud.get_data(db, city=city, skip=skip, limit=limit)
    return data


'''----------------------------------------------------------'''


'''--------------- jinja2模板渲染前端页面 ---------------'''


from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

templates = Jinja2Templates(directory='covid19/template')

# 该接口前后端不分离，使用模板引擎。要么通过城市名称展示数据，要么就是个默认页面直接取前100条数据展示
@application.get('/')
def covid(request: Request, city:str = None, skip:int=0, limit:int=100, db: Session = Depends(get_db)):
    data = crud.get_data(db, city=city, skip=skip, limit=limit)    # 该函数返回的是一个可迭代对象，可用for循环一条条展示
    # 第一个参数是数据要返回的页面，第二个参数是要传递给模板的数据
    return templates.TemplateResponse('home.html', {
        'request': request, 
        'data': data,
        'sync_data_url':'covid19/sync_coronavirus_data/jhu'
        })
