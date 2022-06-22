#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   crud.py    
@License :   (C)Copyright 2021 , atomsocial

如果出现了mysql错误：pymysql.err.OperationalError: (1205, 'Lock wait timeout exceeded; try restarting transaction') 错误
请执行下面两句话，进行会话kill
select * from information_schema.innodb_trx;
kill XXXX

接口中注意silence参数要使用object 传参的方式
'''
from msilib.schema import Error
import re
from datetime import datetime
from typing import List

from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm import Session
from .base import Base as TableBase
from sqlalchemy import desc, asc
from sqlalchemy.orm.query import Query
from typing import Any
import time
from sqlalchemy.dialects.mysql import insert
import operator
from functools import reduce


class MysqlError(Exception):
    pass

def _decorate_excepthon(origin_func):
    """
    目前主要用于数据更新和数据插入的异常拦截
    :param origin_func:
    :return:
    """

    def wrapper(*args, **kw):
        # 需要对参数的顺序进行唯一化调整
        try:
            return origin_func(*args, **kw)
        except IntegrityError as e:
            if kw and "silence" in kw and kw.get("silence"):
                return None
            err_str = e.orig.args[1]
            if e.orig.args[0] == 1452:
                # err_str='Cannot add or update a child row: a foreign key constraint fails (`atom`.`users`, CONSTRAINT `users_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organization` (`id`))'
                if err_str.startswith("Cannot add or update a child row: a foreign key constraint fails"):
                    print("外键约束错误")  # XXX 约束XXX
                    a = re.compile(
                        "[\w\W]+?\(`(?P<database>\w+?)`\.`(?P<table_child>\w+?)`, CONSTRAINT `\w+?` FOREIGN KEY \(`(?P<table_child_seg>\w+?)`\) REFERENCES `(?P<table_parent>\w+?)` \(`(?P<table_parent_seg>\w+?)`\)\)")
                    regMatch = a.match(err_str)
                    if regMatch:
                        result = regMatch.groupdict()
                        print(result)
                        raise MysqlError(
                            "数据录入错误",
                            data={"orig": e.orig.args,
                                  "message": f"外键约束错误({result['table_parent']}.{result['table_parent_seg']}可能不存在)",
                                  "table": result.get("table_child", ""),
                                  "segment": result.get("table_child_seg", ""),
                                  })
            elif e.orig.args[0] == 1062:  # 唯一字段检查
                a = re.compile(
                    "Duplicate entry '[\w]+' for key '(?P<table_child_seg>\w+?)'")
                regMatch = a.match(err_str)
                if regMatch:
                    result = regMatch.groupdict()
                    raise MysqlError(
                        "数据录入错误",
                        data={"orig": e.orig.args, "message": f"表中已经存在{result['table_child_seg']}",
                              "table": result.get("table_child", ""),
                              "segment": result.get("table_child_seg", ""),
                              })
            else:
                raise (e)
        except DataError as e:
            # pymysql.err.DataError: (1406, "Data too long for column 'group' at row 1")
            err_str = e.orig.args[1]
            if e.orig.args[0] == 1406:  # 唯一字段检查
                a = re.compile("Data too long for column '(?P<table_child_seg>\w+?)' at[\w\W]+?")
                regMatch = a.match(err_str)
                if regMatch:
                    table_child_seg = regMatch.groupdict().get("table_child_seg")
                    raise MysqlError(f'数据更新失败', data={"orig": e.orig.args,
                                                      "message": f"{table_child_seg}字段长度过长。长度为{len(e.params.get(table_child_seg, ''))}",
                                                      "table": "",
                                                      "segment": table_child_seg,
                                                      })
        finally:
            args[0].session.commit()  # 一定要加这句话，否则可能会导致trx_mysql_thread

    return wrapper


from typing import Dict, Generic, TypeVar, Type, Union, Tuple

ModelType = TypeVar("ModelType", bound=TableBase)


class BaseOp(Generic[ModelType]):
    """
    sqlalchemy 的基本的增删改查

    关键词查找： https://www.cnblogs.com/kaerxifa/p/13476317.html
    忽略大小写： https://www.cnblogs.com/shengulong/p/9521598.html

    Generic[] 用于编程的时候的类型提示，非常好用。有时候父类是不知道子类要返回的具体的示例字段的。
    尤其是多个mysql 操作表，继承同一个父类，使用父类中的find_one 方法，这时候，父类不知道子类的实例是哪一个的。
    """

    def __init__(self, session: Session, model: Type[ModelType]):
        self.model = model
        self.session = session

    def make_filter_para(self, *args, **kw):
        """
        把 filter_by 或者 filter 的参数统一转化为filter 参数。要求：model 必须是默认的model
        :param args:
        :param kw:
        :return:
        """
        filter_para = [*args]
        for k in kw:
            filter_para.append(getattr(self.model, k) == kw[k])
        return filter_para

    def make_query(self, *args, **kw) -> Query:
        if len(args) == 0:
            return self.session.query(self.model).filter_by(**kw)
        return self.session.query(self.model).filter(*self.make_filter_para(*args, **kw))

    def find_one(self, *args, **kw) -> ModelType:
        model_instance = self.make_query(*args, **kw).first()
        if model_instance is not None:
            self.session.refresh(model_instance)
        return model_instance

    def find(self, *args, page_index: int = 0, page_size=0, sort_by="created_t", is_desc=True, **kw) -> Union[
        List[ModelType], Tuple[int, List[ModelType]]]:
        query = self.make_query(*args, **kw)
        if page_size and page_index:
            return query.count(), query.order_by(desc(sort_by) if is_desc else asc(sort_by)).offset(
                page_size * (page_index - 1)).limit(page_size).all()
        else:
            return query.all()

    def distinct(self, seg, *criterion, page_index: int = 0, page_size=0, sort_by="created_t", is_desc=True, **kw) -> \
            Union[List[str], Tuple[int, List[str]]]:
        if len(criterion) == 0:
            query = self.session.query(seg).filter_by(**kw)
        else:
            query = self.session.query(seg).filter(*self.make_filter_para(*criterion, **kw))
        # query=self.make_query(*criterion,**kw)
        if page_index and page_size:
            start = page_size * (page_index - 1)
            return query.distinct(seg).count(), reduce(operator.add,
                                                       query
                                                       .order_by(desc(sort_by) if is_desc else asc(sort_by))
                                                       .offset(page_size * (page_index - 1))
                                                       .distinct(seg)[start:start + page_size] or [[]]
                                                       )
        return reduce(operator.add, query.distinct(seg).all() or [[]])

    def count(self, *criterion, **kw) -> int:
        return self.make_query(*criterion, **kw).count()

    def add_from_model(self, model_instance: ModelType, silence: bool = False) -> ModelType:
        # 添加到session
        self.session.add(model_instance)
        # 提交
        self.session.commit()
        self.session.refresh(model_instance)
        return model_instance

    def refresh_model(self, model_instance: ModelType, silence: bool = False) -> ModelType:
        self.session.refresh(model_instance)
        return model_instance

    def bulk_insert(self, mappings: List[Dict]):
        """
        批量插入，如果插入不进去就报错
        :param mappings:
        :return:
        """
        self.session.bulk_insert_mappings(self.model, mappings)
        self.session.commit()

    # def remove_from_model(self,model_instance:ModelType)->ModelType:
    #     # 添加到session
    #     self.session.delete(model_instance)
    #     # 提交
    #     self.session.commit()
    #     self.session.refresh(model_instance)
    #     return model_instance

    def remove(self, *criterion, **kw):
        query = self.make_query(*criterion, **kw)
        count = query.delete(synchronize_session="evaluate")
        self.session.commit()
        return count

    def bulk_insert_ignore(self, mappings: List[Dict]):
        """
        有的话就忽略，没有的话就添加
        :param mappings:
        :return:
        """
        self.session.execute(
            self.model.__table__.insert().prefix_with(" ignore"),
            mappings
        )
        self.session.commit()

    def _process_on_duplicate_key_update(self, data: List[Dict], upsert_col: List[str] = None):
        if not upsert_col:
            upsert_col = list(data[0].keys())
        insert_stmt = insert(self.model).values(
            data)
        upsert_para = {}
        for col_name in upsert_col:
            upsert_para[col_name] = getattr(insert_stmt.inserted, col_name)
        return insert_stmt.on_duplicate_key_update(
            **upsert_para
        )

    def bulk_insert_update(self, mappings: List[Dict], upsert_col: List[str] = None):
        """
        有就更新，没有就添加
        :param mappings:
        :param upsert_col:
        :return:
        """
        on_duplicate_key_stmt = self._process_on_duplicate_key_update(mappings, upsert_col)
        self.session.execute(on_duplicate_key_stmt)
        self.session.commit()

    def add_update(self, upsert_col: List[str] = None, **kw):
        """
        单条数据的插入：  有就更新,没有就添加
        Note: 可能导致主键跟着修改
        :return:
        """
        on_duplicate_key_stmt = self._process_on_duplicate_key_update([kw], upsert_col)
        self.session.execute(on_duplicate_key_stmt)
        self.session.commit()

    def add_update_with_result(self, pk_value, pk_seg="id", **kw):
        """
        先查询是否有相关的数据，如果是插入，返回True, 更新，返回False
        :param pk_value:
        :param pk_seg:
        :param kw:
        :return: insert :True  update:False
        """
        r = False if self.find_one({pk_seg: pk_value}) else True
        self.add_update(**kw)
        return r

    def bulk_update(self, mappings: List[Dict]):
        """
        只用于批量更新，不会插入数据
        :param mappings:
        :return:
        """
        self.session.bulk_update_mappings(self.model, mappings)
        self.session.commit()

    def update_from_model(self, model_instance: ModelType, silence: bool = False) -> ModelType:
        return self.add_from_model(model_instance, silence=silence)

    @_decorate_excepthon
    def update(self, *criterion, usd_set: Dict, **kw):
        """
        用于根据某些条件，批量更新某些字段
        :param usd_set:  参数用于数据的更新。其他两个参数用于条件的筛选
        :param criterion:
        :param kw:
        :return:
        """
        self.make_query(*criterion, **kw).update(usd_set, synchronize_session=False)
        self.session.commit()


    def now_times(self) -> dict:
        created_time = datetime.now()
        return dict(storage_time=created_time,
                    storage_t=int(created_time.timestamp()))

#
# # filter 查询条件
# # 1.equal
# res = session.query(Article).filter(Article.id == 21).first()
#
# # 2.notequal
# res = session.query(Article).filter(Article.id != 21).all()
#
# # 3.like & ilike不区分大小写
# res = session.query(Article).filter(Article.title.like('title%')).all()
#
# # 4.in
# res = session.query(Article).filter(Article.title.in_(['title0', 'title1'])).all()
#
# # 5.not in
# res = session.query(Article).filter(~Article.title.in_(['title0', 'title1'])).all()
# res = session.query(Article).filter(Article.title.notin_(['title0', 'title1'])).all()
#
# # 6.isnull
# res = session.query(Article).filter(Article.content == None).all()
#
# # 7.is not null
# res = session.query(Article).filter(Article.content != None).all()
#
# # 8 and
# res = session.query(Article).filter(Article.content == None, Article.title.notin_(['title0', 'title1'])).all()
# res = session.query(Article).filter(and_(Article.content == None, Article.title.notin_(['title0', 'title1']))).all()
#
# # 9 or
# res = session.query(Article).filter(
#     or_(Article.content != None, Article.title.notin_(['title0', 'title1', 'title5']))).all()
