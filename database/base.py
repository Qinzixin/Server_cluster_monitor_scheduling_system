from sqlalchemy.ext.declarative import declarative_base

from enum import Enum
from typing import List
import json


class BaseModelMixin:
    """ 为所有Model提供公用方法 """

    # @declared_attr
    # def id(self):
    #     return Column(String(32), primary_key=True, default=uuid.uuid4().hex)  # 唯一性的UUID

    def get_columns(self):
        d = []
        for column in self.__table__.columns:
            d.append(column.name)
        return d

    def _to_dict(self):
        d = {}
        for column in self.get_columns():
            r = getattr(self, column)
            if isinstance(r, Enum):
                r = r.value
            d[column] = r
        return d

    def to_dict(self):
        return self._to_dict()

    def _which_paras_use_json_load(self, paras: List):
        r = self._to_dict()
        if not paras:
            return r
        try:
            for para in paras:
                if not isinstance(r.get(para, "{}"), str):
                    continue
                r[para] = json.loads(r.get(para, "{}"))
        except Exception as e:
            pass
        return r


# 创建基本映射类
Base = declarative_base(cls=BaseModelMixin)

