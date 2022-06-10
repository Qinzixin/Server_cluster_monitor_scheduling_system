
from pykafka import KafkaClient
from pykafka.common import OffsetType
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('consumer')
patience = 1000

class Consumer:
    def __init__(self,config=None):
        if config is None:
            with open("config.json","r") as f:
                config = json.load(f)
        logger.info('Connecting to Kafka......')
        self.client = KafkaClient(hosts=config["kafka_info"])
        logger.info('Connected.')

    def consume(self, topic_name, database_name='test', consumer_group="secondGroup"):
        
        topic = self.client.topics[topic_name]

        consumer = topic.get_simple_consumer(consumer_group=consumer_group,
                                            consumer_timeout_ms=200,
                                            auto_commit_enable=True,
                                            auto_offset_reset=OffsetType.LATEST,
                                            reset_offset_on_start=False)
        # db = DBManager(database_name=database_name)

        count = 0
        messages = []
        time = None
        while True:
            for message in consumer:
                if message is not None:
                    logger.info("offset: {}, message: {}".format(message.offset, 
                                                                message.value.decode('utf-8')))
                    
                    count += 1
                    # offset, sql_data, time = match_message(message)
                    # messages.append(sql_data)
                    if count > patience:
                        break
            if time is not None:
                year, month, day = time
                # 存入数据库
                # db.trans_blocks2mysql(f"behavior_{year}_{month}_{day}", messages)
            time = None
            messages = []
            count = 0

if __name__ == '__main__':
    Consumer().consume(topic_name='client_info', database_name="", consumer_group='secondGroup')

