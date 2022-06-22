from sqlalchemy.orm import Session
from database.models import Server
from database.crud import BaseOp
from datetime import datetime, timedelta
from enum import Enum


class ServerCrud(BaseOp[Server]):
    def __init__(self, session: Session):
        self.session = session
        super().__init__(session, Server)


class ReportType(Enum):
    YEAR = "YEAR"
    MONTH = "MONTH"
    WEEK = "WEEK"
    DAY = "DAY"
    HOUR = "HOUR"


class DateEncoder:
    @staticmethod
    def encode(date: datetime, flag: ReportType) -> int:
        if flag == ReportType.YEAR:
            time_str = date.strftime("%Y")
        elif flag == ReportType.MONTH:
            time_str = date.strftime("%Y%m")
        elif flag == ReportType.WEEK:
            time_str = (date - datetime(2022, 5, 2)).days // 7
        elif flag == ReportType.DAY:
            time_str = date.strftime("%Y%m%d")
        else:
            time_str = date.strftime("%Y%m%d%H")
        return int(time_str)

    @staticmethod
    def decode(code: int, flag: ReportType) -> datetime:
        """
        想了想，好像没必要把时间从标号转为现实时间
        """
        if flag == ReportType.YEAR:
            date = datetime(year=code, month=1, day=1)
        elif flag == ReportType.MONTH:
            date = datetime(year=code // 100, month=code % 100, day=1)
        elif flag == ReportType.WEEK:
            date = datetime(year=2022, month=5, day=2) + timedelta(days=7 * code)
        elif flag == ReportType.DAY:
            date = datetime(year=code // 10000, month=code // 100 % 100, day=code % 100)
        else:
            date = datetime(year=code // 1000000, month=code // 10000 % 100, day=code // 100 % 100, hour=code % 100)
        return date


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    from database.models import DBSession

    # 创建数据库连接
    session = DBSession()
    crud = ServerCrud(session)
    server1 = Server(name="138", address="172.31.41.138")
    # crud.add_from_model(server1)
    # 单条件查询
    server2 = crud.find_one(name="139")
    # 多条件联合查询
    server3 = crud.find_one(name="139", pk=3)
    if server3 is not None:
        print(server3.name)
    # 修改值
    server3.hdd_limit = 35236
    # 更新数据库
    server4 = crud.update_from_model(server3)
    if server4 is not None:
        print(server4.name)
    session.close()
