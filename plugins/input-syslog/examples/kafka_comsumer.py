import argparse
import json
from kafka import KafkaConsumer, KafkaProducer


parser = argparse.ArgumentParser(description='user input')
parser.add_argument("--kafka", dest="kafka_addr",
                    help="Provide Kafka Addr : localhost:9092")
parser.add_argument("--topic", dest="topic", default='events',
                    help="Specify which topic to listen")
parser.add_argument("--event", dest="event", help="Filter a specific topic")

args = parser.parse_args()

consumer = KafkaConsumer(bootstrap_servers=args.kafka_addr,
                         auto_offset_reset='earliest')
consumer.subscribe([args.topic])

for message in consumer:

    ## Decode JSON
    msg = json.loads(message.value)

    if args.event:
        if msg['event'] and msg['event'] == args.event:
            print (msg)
    else:
        print message
