import os
import json
from kafka import KafkaConsumer, KafkaProducer
from prediction import predict

KAFKA_BOOTSTRAP_SERVER = os.getenv('KAFKA_BOOTSTRAP_SERVER')
KAFKA_CONSUMER_GROUP = 'object-detection-consumer-group'
KAFKA_CONSUMER_TOPIC = os.getenv('KAFKA_TOPIC_IMAGES')
KAFKA_PRODUCER_TOPIC = os.getenv('KAFKA_TOPIC_OBJECTS')


def main():
    # Normally, we'd never want to lose a message,
    # but we want to ignore old messages for this demo, so we set
    # enable_auto_commit=False
    # auto_offset_reset='latest' (Default)
    # This has the effect of starting from the last message.

    consumer = KafkaConsumer(KAFKA_CONSUMER_TOPIC,
                             group_id=KAFKA_CONSUMER_GROUP,
                             bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
                             enable_auto_commit=False,
                             api_version_auto_timeout_ms=30000,
                             request_timeout_ms=450000)

    producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
                             api_version_auto_timeout_ms=30000,
                             max_block_ms=900000,
                             request_timeout_ms=450000,
                             acks='all')

    print(f'Subscribed to "{KAFKA_BOOTSTRAP_SERVER}" consuming topic "{KAFKA_CONSUMER_TOPIC}, producing messages on topic "{KAFKA_PRODUCER_TOPIC}"...')

    try:
        for record in consumer:
            print("Image received... ", end="")
            msg = record.value.decode('utf-8')
            dict = json.loads(msg)
            result = predict(dict)
            print("Image analyzed... ", end="")
            dict['prediction'] = result
            producer.send(KAFKA_PRODUCER_TOPIC, json.dumps(dict).encode('utf-8'))
            producer.flush()
            print("Objects sent back.")
    finally:
        print("Closing KafkaTransformer...")
        consumer.close()
    print("Kafka transformer stopped.")


if __name__ == '__main__':
    main()
