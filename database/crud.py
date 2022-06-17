from typing import Dict, List


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

    @_decorate_excepthon
    def add_from_model(self, model_instance: ModelType, silence: bool = False) -> ModelType:
        # 添加到session
        self.session.add(model_instance)
        # 提交
        self.session.commit()
        self.session.refresh(model_instance)
        return model_instance

    @_decorate_excepthon
    def refresh_model(self, model_instance: ModelType, silence: bool = False) -> ModelType:
        self.session.refresh(model_instance)
        return model_instance

    @_decorate_excepthon
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

    @staticmethod
    def get_table_data(base_query, base_filters: List, time_field, keyword_field, page_index: int = 1,
                       page_size: int = 10,
                       since: int = 0, until: int = 0, keyword: str = "", sort_by="created_t", is_desc=True
                       , return_query=False) -> (int, Any):
        my_filters = base_filters
        if keyword and keyword.strip():
            my_filters.append([keyword_field.like(f"%{keyword.strip()}%")])
        if since:
            until = int(time.time()) if not until else until
            my_filters += [time_field >= since, time_field <= until]
            my_filter = base_query.filter(*my_filters)
            total = my_filter.count()
            # 热度的话，暂时定义为 repost_num、comment_num、like_num 三个值的降序排列
            my_filter = my_filter.order_by(desc(sort_by) if is_desc else asc(sort_by))

        else:  # 按照页获取数据
            my_filter = base_query.filter(*my_filters)
            total = my_filter.count()
            my_filter = my_filter.order_by(desc(sort_by) if is_desc else asc(sort_by)).offset(
                page_size * (page_index - 1)).limit(page_size)
        return total, my_filter.all() if not return_query else my_filter

    def now_times(self) -> dict:
        created_time = datetime.now()
        return dict(storage_time=created_time,
                    storage_t=int(created_time.timestamp()))