# 导入:
from email.policy import default
import pymysql
from sqlalchemy import Column, Date, DateTime, Float, String, create_engine
from sqlalchemy.orm import sessionmaker
import settings
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
    gpu_num = Column(Integer, comment="GPU数量")
    gpus = relationship("GPU")


class GPU(Base):
    __tablename__ = "gpu"
    pk = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment="主键")
    name = Column(String(40), nullable=False, comment="gpu名称,例如RTX 3090ti")
    cuda_version = Column(String(10), default="cuda10.1", comment="服务器的cuda版本")
    server_id = Column(Integer, ForeignKey("server.pk"))


class HourInfo(Base):
    __tablename__ = "hour_info"
    pk = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment="主键")
    identity = Column(Integer, nullable=False, comment="标识周数 = （归档时间 - 2022.1.1:00）+1")
    created_time = Column(DateTime, unique=True, comment="写入数据库的时间")
    server = Column(Integer, ForeignKey("server.pk"), comment="归档的服务器")

    hdd_used_avg = Column(BigInteger, comment="平均硬盘空间使用率")
    network_up_total = Column(BigInteger, comment="网络上传流量 总量")
    network_down_total = Column(BigInteger, comment="网络下载流量 总量")
    memory_avg = Column(BigInteger, comment="内存平均使用率 ")
    gpu_memory_avg = Column(Float, comment="gpu显存平均使用率")
    idle_rate = Column(Float, comment="空闲比率 ")
    day_id = Column(Integer, ForeignKey("DayInfo.pk"))


class DayInfo(Base):
    __tablename__ = "day_info"
    pk = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment="主键")
    identity = Column(String(40), nullable=False, comment="标识汇总的字符串,如, 2022-2-3")
    created_time = Column(DateTime, unique=True, comment="写入数据库的时间")
    server = Column(Integer, ForeignKey("server.pk"), comment="归档的服务器")

    hdd_used_avg = Column(BigInteger, comment="平均硬盘空间使用率")
    network_up_total = Column(BigInteger, comment="网络上传流量 总量")
    network_down_total = Column(BigInteger, comment="网络下载流量 总量")
    memory_avg = Column(BigInteger, comment="内存平均使用率 ")
    gpu_memory_avg = Column(Float, comment="gpu显存平均使用率")
    idle_rate = Column(Float, comment="空闲比率 ")
    week_id = Column(Integer, ForeignKey("WeekInfo.pk"))
    month_id = Column(Integer, ForeignKey("MonthInfo.pk"))
    year_id = Column(Integer, ForeignKey("YearInfo.pk"))
    hours = relationship("HourInfo")


class WeekInfo(Base):
    __tablename__ = "week_info"
    pk = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment="主键")
    identity = Column(Integer, nullable=False, comment="标识周数 = （归档时间 - 2022.1.1）//7+1")
    created_time = Column(DateTime, unique=True, comment="写入数据库的时间")
    server = Column(Integer, ForeignKey("server.pk"), comment="归档的服务器")

    hdd_used_avg = Column(BigInteger, comment="平均硬盘空间使用率")
    network_up_total = Column(BigInteger, comment="网络上传流量 总量")
    network_down_total = Column(BigInteger, comment="网络下载流量 总量")
    memory_avg = Column(BigInteger, comment="内存平均使用率 ")
    gpu_memory_avg = Column(Float, comment="gpu显存平均使用率")
    idle_rate = Column(Float, comment="空闲比率 ")
    week_id = Column(Integer, ForeignKey("ReportWeek.pk"))
    days = relationship("DayInfo")


class MonthInfo(Base):
    __tablename__ = "month_info"
    pk = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment="主键")
    identity = Column(String(40), nullable=False, comment="标识汇总的字符串,如, 2022-2-3")
    created_time = Column(DateTime, unique=True, comment="写入数据库的时间")
    server = Column(Integer, ForeignKey("server.pk"), comment="归档的服务器")

    hdd_used_avg = Column(BigInteger, comment="平均硬盘空间使用率")
    network_up_total = Column(BigInteger, comment="网络上传流量 总量")
    network_down_total = Column(BigInteger, comment="网络下载流量 总量")
    memory_avg = Column(BigInteger, comment="内存平均使用率 ")
    gpu_memory_avg = Column(Float, comment="gpu显存平均使用率")
    idle_rate = Column(Float, comment="空闲比率 ")
    month_id = Column(Integer, ForeignKey("ReportMonth.pk"))
    days = relationship("DayInfo")


class YearInfo(Base):
    """
    单台服务器的年度信息汇总
    """
    __tablename__ = "year_info"
    pk = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment="主键")
    identity = Column(String(40), nullable=False, comment="标识汇总的字符串,如, 2022-2-3")
    created_time = Column(DateTime, unique=True, comment="写入数据库的时间")
    server = Column(Integer, ForeignKey("server.pk"), comment="归档的服务器")

    hdd_used_avg = Column(BigInteger, comment="平均硬盘空间使用率")
    network_up_total = Column(BigInteger, comment="网络上传流量 总量")
    network_down_total = Column(BigInteger, comment="网络下载流量 总量")
    memory_avg = Column(BigInteger, comment="内存平均使用率 ")
    gpu_memory_avg = Column(Float, comment="gpu显存平均使用率")
    idle_rate = Column(Float, comment="空闲比率 ")
    year_id = Column(Integer, ForeignKey("ReportYear.pk"))
    days = relationship("DayInfo")


class ReportWeek(Base):
    """
    周报，所有服务器的周度信息汇总
    """
    __tablename__ = "report_week"
    pk = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment="主键")
    identity = Column(String(40), nullable=False, comment="标识汇总的字符串,如, 2022-2-3")
    created_time = Column(DateTime, unique=True, comment="归档的日期,可以代表归档的周数")
    busy_server1 = Column(Integer, ForeignKey("server.pk"), comment="最忙服务器")
    busy_server2 = Column(Integer, ForeignKey("server.pk"), comment="最忙服务器")
    busy_server3 = Column(Integer, ForeignKey("server.pk"), comment="最忙服务器")
    idle_server1 = Column(Integer, ForeignKey("server.pk"), comment="最闲服务器")
    idle_server2 = Column(Integer, ForeignKey("server.pk"), comment="最闲服务器")
    idle_server3 = Column(Integer, ForeignKey("server.pk"), comment="最闲服务器")
    server_weeks = relationship("WeekInfo")


class ReportMonth(Base):
    __tablename__ = "report_month"
    pk = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment="主键")
    identity = Column(String(40), nullable=False, comment="标识汇总的字符串,如, 2022-2-3")
    created_time = Column(DateTime, unique=True, comment="归档的日期,可以代表归档的周数")
    busy_server1 = Column(Integer, ForeignKey("server.pk"), comment="最忙服务器")
    busy_server2 = Column(Integer, ForeignKey("server.pk"), comment="最忙服务器")
    busy_server3 = Column(Integer, ForeignKey("server.pk"), comment="最忙服务器")
    idle_server1 = Column(Integer, ForeignKey("server.pk"), comment="最闲服务器")
    idle_server2 = Column(Integer, ForeignKey("server.pk"), comment="最闲服务器")
    idle_server3 = Column(Integer, ForeignKey("server.pk"), comment="最闲服务器")
    server_months = relationship("MonthInfo")


class ReportYear(Base):
    __tablename__ = "report_year"
    pk = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment="主键")
    identity = Column(String(40), nullable=False, comment="标识汇总的字符串,如, 2022-2-3")
    created_time = Column(DateTime, unique=True, comment="归档的日期,可以代表归档的周数")
    busy_server1 = Column(Integer, ForeignKey("server.pk"), comment="最忙服务器")
    busy_server2 = Column(Integer, ForeignKey("server.pk"), comment="最忙服务器")
    busy_server3 = Column(Integer, ForeignKey("server.pk"), comment="最忙服务器")
    idle_server1 = Column(Integer, ForeignKey("server.pk"), comment="最闲服务器")
    idle_server2 = Column(Integer, ForeignKey("server.pk"), comment="最闲服务器")
    idle_server3 = Column(Integer, ForeignKey("server.pk"), comment="最闲服务器")
    server_years = relationship("YearInfo")


engine = create_engine(
    f'mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}')
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
    server1 = Server(name="139", address="172.31.41.139", memory_limit=115389480, hdd_limit=7930348,
                     cuda_version="CUDA11.4",
                     location="唐山机房", gpu_num=4)
    session = DBSession()
    session.add(server1)
    session.commit()
    session.refresh(server1)
    gpu1 = GPU(name="A4000", cuda_version="cuda11.4", server_id=server1.pk)
    session.add(gpu1)
    session.commit()
    session.refresh(gpu1)
    print(gpu1)


if __name__ == "__main__":
    init()
