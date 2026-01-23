
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


SQLALCHEMY_DATABASE_URL = 'sqlite:///./covid19.sqlite3'            # MySQL数据库的写法
# SQLALCHEMY_DATABASE_URL = 'postgresql://user:password@host:port/database_name'        # PostgreSQL数据库的写法


engine = create_engine(
    # echo=True表示引擎将用repr()函数记录所有语句及其参数列表到日志
    # 由于SQLAlchemy是多线程，指定check_same_thread=False来让建立的对象任意线程都可使用。这个参数只在用SQLite数据库时设置
    SQLALCHEMY_DATABASE_URL,    # 数据库的URL
    echo=True,                  # 记录所有语句到日志里
    connect_args={'check_same_thread': False}
)

# 在SQLAlchemy中，CRUD都是通过会话(session)进行的，所以我们必须要先创建会话，每一个SessionLocal实例就是一个数据库session
# flush()是指发送数据库语句到数据库，但数据库不一定执行写入磁盘；commit()是指提交事务，将变更保存到数据库文件
SessionLocal = sessionmaker(bind=engine,autocommit=False, autoflush=False, expire_on_commit=True)


# 创建基本映射类
Base = declarative_base(name='Base')