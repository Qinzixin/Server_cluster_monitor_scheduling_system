from typing import Optional

from pydantic import BaseModel, Field, Json
from datetime import datetime

BigInteger = int
Float = float


class ServerReturn(BaseModel):
    """
    Resource验证类
    """
    pk: int = Field(0, description="此项可不填，服务器主键")
    name: str = Field(..., description="服务器名称")
    address: str = Field(..., description="ip")
    description: Optional[str] = Field("", description="此项可不填，服务器描述，用于描述此服务器的一些特征，便于选择")
    memory_limit: int = Field(0, description="内存上限")
    hdd_limit: int = Field(0, description="硬盘空间上限")
    cuda_version: Optional[str] = Field("", description="此项可不填，服务器的cuda版本")
    location: Optional[str] = Field("", description="此项可不填，存放地点")

    class Config:
        orm_mode = True


class GPUReturn(BaseModel):
    pk: Optional[int] = Field(0, description="此项可不填，主键")
    name: str = Field(..., description="gpu名称,例如RTX 3090ti")
    cuda_version: Optional[str] = Field("", description="此项可不填，服务器的cuda版本")
    server_id: Optional[int] = Field(0, description="此项可不填，")

    class Config:
        orm_mode = True


class HourInfoReturn(BaseModel):
    """
    Resource验证类
    """
    pk: Optional[int] = Field(0, description="此项可不填，主键")
    identity: int = Field(..., description="标识周数 = （归档时间 - 2022.1.1:00）+1")
    server: Optional[int] = Field(0, description="此项可不填，归档的服务器")
    hdd_used_avg: BigInteger = Field(..., description="平均硬盘空间使用率")
    network_up_total: BigInteger = Field(..., description="网络上传流量 总量")
    network_down_total: BigInteger = Field(..., description="网络下载流量 总量")
    memory_avg: BigInteger = Field(..., description="内存平均使用率 ")
    gpu_memory_avg: Float = Field(..., description="gpu显存平均使用率")
    idle_rate: Float = Field(..., description="空闲比率 ")
    day_id: Optional[int] = Field(0, description="此项可不填，")

    class Config:
        orm_mode = True


class DayInfoReturn(BaseModel):
    """
    Resource验证类
    """
    pk: Optional[int] = Field(0, description="此项可不填，主键")
    identity: int = Field(..., description="标识汇总的字符串,如, 2022-2-3")
    server: Optional[int] = Field(0, description="此项可不填，归档的服务器")
    hdd_used_avg: BigInteger = Field(..., description="平均硬盘空间使用率")
    network_up_total: BigInteger = Field(..., description="网络上传流量 总量")
    network_down_total: BigInteger = Field(..., description="网络下载流量 总量")
    memory_avg: BigInteger = Field(..., description="内存平均使用率 ")
    gpu_memory_avg: Float = Field(..., description="gpu显存平均使用率")
    idle_rate: Float = Field(..., description="空闲比率 ")
    week_id: Optional[int] = Field(0, description="此项可不填，")
    month_id: Optional[int] = Field(0, description="此项可不填，")
    year_id: Optional[int] = Field(0, description="此项可不填，")

    class Config:
        orm_mode = True


class WeekInfoReturn(BaseModel):
    """
    Resource验证类
    """
    pk: Optional[int] = Field(0, description="此项可不填，主键")
    identity: int = Field(..., description="标识周数 = （归档时间 - 2022.1.1）//7+1")
    server: Optional[int] = Field(0, description="此项可不填，归档的服务器")
    hdd_used_avg: BigInteger = Field(..., description="平均硬盘空间使用率")
    network_up_total: BigInteger = Field(..., description="网络上传流量 总量")
    network_down_total: BigInteger = Field(..., description="网络下载流量 总量")
    memory_avg: BigInteger = Field(..., description="内存平均使用率 ")
    gpu_memory_avg: Float = Field(..., description="gpu显存平均使用率")
    idle_rate: Float = Field(..., description="空闲比率 ")

    class Config:
        orm_mode = True


class MonthInfoReturn(BaseModel):
    """
    Resource验证类
    """
    pk: Optional[int] = Field(0, description="此项可不填，主键")
    identity: str = Field(..., description="标识汇总的字符串,如, 2022-2-3")
    server: Optional[int] = Field(0, description="此项可不填，归档的服务器")
    hdd_used_avg: BigInteger = Field(..., description="平均硬盘空间使用率")
    network_up_total: BigInteger = Field(..., description="网络上传流量 总量")
    network_down_total: BigInteger = Field(..., description="网络下载流量 总量")
    memory_avg: BigInteger = Field(..., description="内存平均使用率 ")
    gpu_memory_avg: Float = Field(..., description="gpu显存平均使用率")
    idle_rate: Float = Field(..., description="空闲比率 ")

    class Config:
        orm_mode = True


class YearInfoReturn(BaseModel):
    """
    Resource验证类
    """
    pk: Optional[int] = Field(0, description="此项可不填，主键")
    identity: str = Field(..., description="标识汇总的字符串,如, 2022-2-3")
    server: Optional[int] = Field(0, description="此项可不填，归档的服务器")
    hdd_used_avg: BigInteger = Field(..., description="平均硬盘空间使用率")
    network_up_total: BigInteger = Field(..., description="网络上传流量 总量")
    network_down_total: BigInteger = Field(..., description="网络下载流量 总量")
    memory_avg: BigInteger = Field(..., description="内存平均使用率 ")
    gpu_memory_avg: Float = Field(..., description="gpu显存平均使用率")
    idle_rate: Float = Field(..., description="空闲比率 ")

    class Config:
        orm_mode = True


class ReportWeekReturn(BaseModel):
    """
    Resource验证类
    """
    pk: Optional[int] = Field(0, description="此项可不填，主键")
    identity: int = Field(..., description="标识汇总的字符串,如, 2022-2-3")
    busy_server1: Optional[int] = Field(0, description="此项可不填，最忙服务器")
    busy_server2: Optional[int] = Field(0, description="此项可不填，第二服务器")
    busy_server3: Optional[int] = Field(0, description="此项可不填，第三服务器")
    idle_server1: Optional[int] = Field(0, description="此项可不填，最闲服务器")
    idle_server2: Optional[int] = Field(0, description="此项可不填，第二服务器")
    idle_server3: Optional[int] = Field(0, description="此项可不填，第三服务器")

    class Config:
        orm_mode = True


class ReportMonthReturn(BaseModel):
    """
    Resource验证类
    """
    pk: Optional[int] = Field(0, description="此项可不填，主键")
    identity: int = Field(..., description="标识汇总的字符串,如, 2022-2-3")
    busy_server1: Optional[int] = Field(0, description="此项可不填，最忙服务器")
    busy_server2: Optional[int] = Field(0, description="此项可不填，第二服务器")
    busy_server3: Optional[int] = Field(0, description="此项可不填，第三服务器")
    idle_server1: Optional[int] = Field(0, description="此项可不填，最闲服务器")
    idle_server2: Optional[int] = Field(0, description="此项可不填，第二服务器")
    idle_server3: Optional[int] = Field(0, description="此项可不填，第三服务器")

    class Config:
        orm_mode = True


class ReportYearReturn(BaseModel):
    """
    Resource验证类
    """
    pk: Optional[int] = Field(0, description="此项可不填，主键")
    identity: int = Field(..., description="标识汇总的字符串,如, 2022-2-3")
    busy_server1: Optional[int] = Field(0, description="此项可不填，最忙服务器")
    busy_server2: Optional[int] = Field(0, description="此项可不填，第二服务器")
    busy_server3: Optional[int] = Field(0, description="此项可不填，第三服务器")
    idle_server1: Optional[int] = Field(0, description="此项可不填，最闲服务器")
    idle_server2: Optional[int] = Field(0, description="此项可不填，第二服务器")
    idle_server3: Optional[int] = Field(0, description="此项可不填，第三服务器")

    class Config:
        orm_mode = True