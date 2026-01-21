'''
FastAPI的依赖注入系统

“依赖注入”是指在编程中，为保证代码成功运行，先导入或声明其所需要的 “依赖”，如子函数、数据库连接等
- 提高代码的复用率
- 共享数据库的连接
- 增强安全、认证和角色管理


'''



from click import Option
from fastapi import APIRouter, Header

app05 = APIRouter()


''' ************** 1. Dependencies 创建、导入和声明依赖 ************** '''

from typing import Optional
from fastapi import Depends

async def common_parameters(q:Optional[str] = None, page:int = 1, limit:int = 100):
    return {"q": q, "page":page, "limit":limit}

@app05.get('/dependency01')
async def dependency01(commons:dict = Depends(common_parameters)):
    return commons
# 依赖是不区分同步函数和异步函数的
@app05.get('/dependency02') # 可以在async def中调用def依赖，也可以在def中导入async def依赖
def dependency02(commons:dict = Depends(common_parameters)):
    return commons


''' ************** 2. Classes as Dependencies 类作为依赖项 ************** '''

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, page: int = 1, limit: int = 100):
        self.q = q
        self.page = page
        self.limit = limit

# 将类作为依赖有三种写法
@app05.get('/classes_as_dependency')
# async def classes_as_dependency(commons:CommonQueryParams = Depends(CommonQueryParams)):  # 写法一
# async def classes_as_dependency(commons:CommonQueryParams = Depends()):   # 写法二
async def classes_as_dependency(commons=Depends(CommonQueryParams)):    # 写法三
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.page-1:commons.page+commons.limit-1]  # 查询数据库
    response.update({"items": items})
    return response


''' ************** 3. Sub-dependencies 子依赖 ************** '''

def query(q:Optional[str]=None):
    # 一些逻辑处理
    pass
    return q

def sub_query(q:str = Depends(query), last_query:Optional[str]=None):
    if not q:
        return last_query
    return q

@app05.get('/sub_dependency')
async def sub_dependency(final_query:str=Depends(sub_query, use_cache=True)):
    """use_cache默认是True, 表示当多个依赖有一个共同的子依赖时，每次request请求只会调用子依赖一次，多次调用将从缓存中获取"""
    return {"sub_dependency": final_query}


''' ************** 4. Dependencies in path operation decorators 路径操作装饰器中的多依赖 ************** '''

from fastapi import Header, HTTPException

async def verify_token(x_token:str=Header(...)):
    """没有返回值的子依赖"""
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")
    return x_token

async def verify_key(x_key:str=Header(...)):
    """有返回值的子依赖，但是返回值不会被调用"""
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key

# 这时候不是在函数参数中调用依赖，而是在路径操作中
@app05.get('/dependency_in_path_operation', dependencies=[Depends(verify_token), Depends(verify_key)])
async def dependency_in_path_operation():
    return [{"user":"user01"},{"user":"user02"}]


''' ************** 5. Global Dependencies 全局依赖 ************** '''

# 希望在应用里面，所有的token和key都要经过校验，调用上面两个子依赖
# app05 = APIRouter(dependencies=[Depends(verify_token), Depends(verify_key)])



''' ************** 6. Dependencies with yield 带yield的依赖 ************** '''

# 以下都是伪代码

# 获取数据库连接，这个方法应该是共享的依赖
async def get_db():
    db = "db_connection"
    try:
        yield db    # 数据库连接成功后，返回db
    finally:
        db.endswith("db_close")  # 关闭数据库连接


async def dependency_a():
    dep_a = "generate_dep_a()"
    try:
        yield dep_a 
    finally:
        dep_a.endswith("db_close")


async def dependency_b(dep_a=Depends(dependency_a)):
    dep_b = "generate_dep_b()"
    try:
        yield dep_b
    finally:
        dep_b.endswith(dep_a)


async def dependency_c(dep_b=Depends(dependency_b)):
    dep_c = "generate_dep_c()"
    try:
        yield dep_c
    finally:
        dep_c.endswith(dep_b)

'''
请问：为什么要用yield，直接使用return不行吗

1、请问共享数据库连接的时候，为什么需要使用yield呢？
2、如果使用return，可以吗？如果可以比yield优势的地方在哪里？
3、共享数据库连接的“共享"怎么理解呢？每次调用session生成函数的时候不都是新生成一个吗，为什么说是"共享"呢


1. yield 虽然也是返回函数结果, 但是相对 return, yield 可以“做到一半”就返回, 并将函数挂起在这个位置, 
等其他事情做完之后, 再回头从这个位置继续往下执行. 这里用 yield, 是因为我是先“连接上数据库”, 可以读数据啊之类的; 
但是这时候前端传回来一组数据, 比如“某件商品的单价”和“商品销售数量”. 我要存的是“销售总额”, 
那么后端可能会计算前两个数据的乘积——这就是“另一件事”. 等这个乘法做完了, 我就可以在当前的数据库连接状态下将数字存进去了

2. return 运行完之后, 函数就跳出了, 不能从“半路”返回去再做. yield 的使用, 极大方便了协程的实现

3. 这个“共享”, 我的理解是一个session 下的所有接口都是“共享”当前的数据库状态. 
新的 session 的建立应该是发生在另一个客户端访问的时候. 当然, 这个“共享”也有可能是所有用户的访问, 
其数据库状态都是同步的? 不是很确定了

'''