# 导入:
from email.policy import default
import pymysql
from sqlalchemy import Column, Date, DateTime, Float, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import enum
import time
from typing import Optional
import settings
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, ForeignKey, String, Enum, BigInteger
from sqlalchemy.orm import relationship
from database.base import Base

# 定义Server对象:
class Server(Base):
    # 表的名字:
    __tablename__ = 'server'

    # 表的结构:
    pk = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment="服务器主键")
    name = Column(String(40), nullable=False, comment="服务器名称")
    address = Column(String(100), nullable=False, unique=True, comment="ip")
    description = Column(String(100), nullable=True, comment="服务器描述，用于描述此服务器的一些特征，便于选择")
    memory_limit = Column(BigInteger, comment="内存上限")
    hdd_limit = Column(BigInteger, comment="硬盘空间上限")
    cuda_version = Column(String(10), default="cuda10.1", comment="服务器的cuda版本")
    location = Column(String(200), nullable=True, comment="存放地点")
    # gpu信息由gpu数量以及gpu型号
    gpu_num =  Column(Integer, comment="GPU数量")
    gpus = relationship("GPU")
    
class GPU(Base):
    __tablename__ = "gpu"
    pk = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment="主键")
    name = Column(String(40), nullable=False, comment="gpu名称,例如RTX 3090ti")
    cuda_version = Column(String(10), default="cuda10.1", comment="服务器的cuda版本")
    server_id = Column(Integer, ForeignKey("server.pk"))


class DayInfo(Base):
    __tablename__ = "day_info"
    pk = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment="主键")
    name = Column(String(40), nullable=False, comment="标识汇总的字符串,如, 2022-2-3")
    date = Column(DateTime, unique=True,comment="归档的日期,可以代表归档的周数")
    server = Column(Integer, ForeignKey("server.pk"), comment="归档的服务器")
    hdd_used_avg = Column(BigInteger, comment="平均硬盘空间使用率")
    network_up_total = Column(BigInteger, comment="网络上传流量 总量")
    network_down_total = Column(BigInteger, comment="网络下载流量 总量")
    memory_avg = Column(BigInteger, comment="内存使用情况 总量，已使用 ")
    busy_time = Column(String(40), nullable=False, comment="最繁忙时段")
    idle_rate = Column(Float, comment="内存使用情况 总量，已使用 ")

class HourInfo(Base):
    __tablename__ = "hour_info"
    pk = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment="主键")
    name = Column(String(40), nullable=False, comment="标识汇总的字符串,如, 2022-2-3")
    date = Column(DateTime, unique=True,comment="归档的日期,可以代表归档的周数")
    server = Column(Integer, ForeignKey("server.pk"), comment="归档的服务器")
    hdd_used_avg = Column(BigInteger, comment="平均硬盘空间使用率")
    network_up_total = Column(BigInteger, comment="网络上传流量 总量")
    network_down_total = Column(BigInteger, comment="网络下载流量 总量")
    memory_avg = Column(BigInteger, comment="内存使用情况 总量，已使用 ")
    busy_time = Column(String(40), nullable=False, comment="最繁忙时段")
    idle_rate = Column(Float, comment="内存使用情况 总量，已使用 ")

class WeekInfo(Base):
    __tablename__ = "week_info"
    pk = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment="主键")
    name = Column(String(40), nullable=False, comment="标识汇总的字符串,如, 2022-2-3")
    date = Column(DateTime, unique=True,comment="归档的日期,可以代表归档的周数")
    server = Column(Integer, ForeignKey("server.pk"), comment="归档的服务器")
    hdd_used_avg = Column(BigInteger, comment="平均硬盘空间使用率")
    network_up_total = Column(BigInteger, comment="网络上传流量 总量")
    network_down_total = Column(BigInteger, comment="网络下载流量 总量")
    memory_avg = Column(BigInteger, comment="内存使用情况 总量，已使用 ")
    busy_time = Column(String(40), nullable=False, comment="最繁忙时段")
    idle_rate = Column(Float, comment="内存使用情况 总量，已使用 ")

class MonthInfo(Base):
    __tablename__ = "month_info"
    pk = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment="主键")
    name = Column(String(40), nullable=False, comment="标识汇总的字符串,如, 2022-2-3")
    date = Column(DateTime, unique=True,comment="归档的日期,可以代表归档的周数")
    server = Column(Integer, ForeignKey("server.pk"), comment="归档的服务器")
    hdd_used_avg = Column(BigInteger, comment="平均硬盘空间使用率")
    network_up_total = Column(BigInteger, comment="网络上传流量 总量")
    network_down_total = Column(BigInteger, comment="网络下载流量 总量")
    memory_avg = Column(BigInteger, comment="内存使用情况 总量，已使用 ")
    busy_time = Column(String(40), nullable=False, comment="最繁忙时段")
    idle_rate = Column(Float, comment="内存使用情况 总量，已使用 ")

class YearInfo(Base):
    __tablename__ = "year_info"
    pk = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment="主键")
    name = Column(String(40), nullable=False, comment="标识汇总的字符串,如, 2022-2-3")
    date = Column(DateTime, unique=True,comment="归档的日期,可以代表归档的周数")
    server = Column(Integer, ForeignKey("server.pk"), comment="归档的服务器")
    hdd_used_avg = Column(BigInteger, comment="平均硬盘空间使用率")
    network_up_total = Column(BigInteger, comment="网络上传流量 总量")
    network_down_total = Column(BigInteger, comment="网络下载流量 总量")
    memory_avg = Column(BigInteger, comment="内存使用情况 总量，已使用 ")
    busy_time = Column(String(40), nullable=False, comment="最繁忙时段")
    idle_rate = Column(Float, comment="内存使用情况 总量，已使用 ")



engine = create_engine(f'mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}')
    # 创建DBSession类型:
DBSession = sessionmaker(bind=engine)

def init():
    try:
        con = pymysql.connect(host=settings.MYSQL_HOST, user=settings.MYSQL_USER, port=settings.MYSQL_PORT,
                            passwd=settings.MYSQL_PASSWD, charset='utf8')
        cursor = con.cursor()
        # 开始建库
        cursor.execute(f"create DATABASE IF NOT EXISTS {settings.MYSQL_DB} character set UTF8MB4  ")
        cursor.close()
        con.close()
    except:
        print("数据库已存在，无需重复创建")
        pass
    # 初始化数据库连接:
    
    Base.metadata.create_all(engine)

    

def test():
    server1 = Server(name="139",address = "172.31.41.139",memory_limit=115389480,hdd_limit=7930348,cuda_version="CUDA11.4",
                            location="唐山机房", gpu_num=4)
    session = DBSession()
    session.add(server1)
    session.commit()
    session.refresh(server1)
    gpu1 = GPU(name="A4000",cuda_version="cuda11.4", server_id=server1.pk)
    session.add(gpu1)
    session.commit()
    session.refresh(gpu1)
    print(gpu1)

if __name__ =="__main__":
    init()