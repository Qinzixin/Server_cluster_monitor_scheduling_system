import redis  # 导入redis 模块

import settings


class Redis:
    _pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=settings.REDIS_PASSWD,
                                 decode_responses=True)

    def __init__(self):
        self.session = redis.Redis(connection_pool=self._pool)

    def set(self, name, value):
        return self.session.set(name, value)

    def setnx(self, name, value):
        return self.session.setnx(name, value)

    def expire(self, name, time):
        return self.session.expire(name, time)

    def ttl(self, name):
        return self.session.ttl(name)

    def pipeline(self, transaction=True, shard_hint=None):
        return self.session.pipeline(transaction, shard_hint)

    def delete(self, *names):
        return self.session.delete(*names)

    def hdel(self, name, *keys):
        return self.session.hdel(name, *keys)

    def get(self, name):
        return self.session.get(name)

    def hset(self, name, key, value):
        return self.session.hset(name, key, value)

    def hget(self, name, key):
        return self.session.hget(name, key)

    def hkeys(self, name):
        return self.session.hkeys(name)

    def keys(self, pattern="*"):
        return self.session.keys(pattern)

    def exists(self, *names):
        return self.session.exists(*names)

    def lpush(self, name, *values):
        return self.session.lpush(name, *values)

    def lrange(self, name, start, end):
        """
        :param name:
        :param start:  -1 表示最后一个元素
        :param end:
        :return:
        """
        return self.session.lrange(name, start, end)

    def ltrim(self, name, start, end):
        return self.session.ltrim(name, start, end)


if __name__ == "__main__":
    red = Redis()
    red.hset("client_info_1","memory_used",48325)
    red.hset("client_info_1","hdd_used",35225)
    red.hset("client_info_1","uptime",62356)
    print(red.hget("client_info_1","hdd_used"))