from sqlalchemy.orm import Session
from database.models import Server
from datetime import datetime, timedelta
from enum import Enum

"""class ServerCrud(BaseOp[Server]):
    def __init__(self, session: Session):

        super().__init__(session, Server)
        self.session = session"""


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
