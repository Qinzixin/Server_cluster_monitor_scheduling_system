from pykafka import KafkaClient
import logging

# Create logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('producer')

class Reporter:
    def __init__(self,config:dict):
        self.pk = config["pk"]
        kafka_info = config["kafka_info"]
        logger.info('Connecting to Kafka......')
        self.client = KafkaClient(hosts=kafka_info)
        logger.info('Connected.')

        topic_name = "client_info"

        # Connect to Topic
        logger.info('Connecting to Topic......')
        self.topic = self.client.topics[topic_name]
        logger.info('Connected.')

    def update_state(self, state):
        # print("now is: ",byte_str(state))
        with self.topic.get_sync_producer() as producer:
            producer.produce(state.encode('utf-8'))
            logger.info("produce message: %s" % state)

    def send(self,state):
        self.update_state(state=state)

if __name__ == "__main__":
    # 单数据源秒级生产者
    produce_messages('event-second', './data/userBehavior_sorted.csv', 'second' )

    # 单数据源小时级生产者
    produce_messages('event-hour', './data/userBehavior_sorted.csv', 'hour' )