import imp
from pykafka import KafkaClient
from pykafka.common import OffsetType
import logging
from datetime import datetime
import happybase
import json
import sys
sys.path.append("..")
from database.redis import * 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('consumer')
patience = 1000

kafka = '10.126.62.37:9093,10.126.62.37:9094,10.126.62.37:9095'
zookeeper = '10.126.62.37:2181'

def create_table(conn, table, families):
    """
    :return: 创建表
    """
    print('Creating table <{}>........'.format(table))
    if bytes(table, 'ascii') in conn.tables():
        print('<{}> already exists.'.format(table))
    else:
        try:
            conn.create_table(table, families)
            print('Successful to create table <{}>'.format(table))
        except:
            print('Failed to create table <{}>'.format(table))

def insert_row_hbase(conn, table, inputs):
    """
    :return: 向hbase中插入数据
    """
    print('Inserting row........')
    # 获得table实例
    table = conn.table(table)

    # 批量发送数据 每一批最多十条
    with table.batch(batch_size=1) as bat:
        line_dic = json.loads(inputs.decode().strip())

        habse_ms_dic = {}
        
        habse_ms_dic['cf1:Pk'] = str(line_dic["pk"])
        habse_ms_dic['cf1:Time'] = str(line_dic["time"])
        habse_ms_dic['cf1:Memory_total'] = str(line_dic["memory_used"])
        habse_ms_dic['cf1:Memory_used'] = str(line_dic["hdd_used"])
        habse_ms_dic['cf1:Hdd_total'] = str(line_dic["hdd_total"])
        habse_ms_dic['cf1:Hdd_used'] = str(line_dic["hdd_used"])
        habse_ms_dic['cf1:Cpu'] = str(line_dic["cpu"])
        habse_ms_dic['cf1:Network_in'] = str(line_dic["network_in"])
        habse_ms_dic['cf1:Network_out'] = str(line_dic["network_out"])
        gpu_count = 0
        for i in range(len(line_dic["gpu_status"])):
            habse_ms_dic[f'cf1:Gpu_{i}_used'] = str(line_dic["gpu_status"][i][2])
            gpu_count += 1
        for i in range(len(line_dic["gpu_status"])):
            habse_ms_dic[f'cf1:Gpu_{i}_total'] = str(line_dic["gpu_status"][i][3])
        habse_ms_dic['cf1:Gpu_count'] = str(gpu_count)
            

        rowkey =  str(line_dic["time"])
        bat.put(rowkey, habse_ms_dic)

def insert_row_redis(red, inputs):
    """
    :return: 向redis中插入数据
    """
    print('Inserting row........')

    line_dic = json.loads(inputs.decode().strip())

    red.hset("client_info_1","pk",line_dic["pk"])
    red.hset("client_info_1","time",line_dic["time"])
    red.hset("client_info_1","memory_total",line_dic["memory_total"])
    red.hset("client_info_1","memory_used",line_dic["memory_used"])
    red.hset("client_info_1","hdd_total",line_dic["hdd_total"])
    red.hset("client_info_1","hdd_used",line_dic["hdd_used"])
    red.hset("client_info_1","cpu",line_dic["cpu"])
    red.hset("client_info_1","network_in",line_dic["network_in"])
    red.hset("client_info_1","network_out",line_dic["network_out"])

    for i in range(len(line_dic["gpu_status"])):
        red.hset("client_info_1",f"gpu_{i}_used",line_dic["gpu_status"][i][2])
    for i in range(len(line_dic["gpu_status"])):
        red.hset("client_info_1",f"gpu_{i}_total",line_dic["gpu_status"][i][3])

    return 1
    

def init_client():
    logger.info('Connecting to Kafka......')
    client = KafkaClient(hosts=kafka,broker_version='0.8.2.1')
    logger.info('Connected.')
    return client

def consumer(topic_name,con,red):
    client = init_client()
    
    topic = client.topics[topic_name]

    # consumer = topic.get_simple_consumer(consumer_group="mykafkaGroup",
    #                                      consumer_timeout_ms=200,
    #                                      auto_commit_enable=True,
    #                                      auto_offset_reset=OffsetType.LATEST,
    #                                      reset_offset_on_start=False)
    consumer  = topic.get_simple_consumer(auto_commit_enable=True,auto_commit_interval_ms=1)

    count = 0
    while True:
        for message in consumer:
            if message is not None:
                logger.info("offset: {}, message: {}".format(message.offset, 
                                                             message.value.decode('utf-8')))
                meassage_value = message.value

                insert_row_hbase(con,'hbase_info_1_2',meassage_value)

                insert_row_redis(red,meassage_value)
                
                count += 1
                print(message.value)
        count = 0

if __name__ == '__main__':
    # con = happybase.Connection('10.126.62.37',9494, autoconnect=False)  # 默认9090端口
    con = happybase.Connection('172.31.41.139',9090, autoconnect=False)
    con.open()  # 打开thrift传输'TCP连接

    red = Redis()
    families = {
        'cf1': dict(max_versions=1),
    }
    create_table(con, 'hbase_info_1_2', families)
    # 秒级消费者
    consumer(topic_name='client_info_1',con=con,red=red)

