import boto3
import random
import argparse

parser = argparse.ArgumentParser(description="Add requests to cnd_queue.fifo")
parser.add_argument('d_val', metavar='D', type=int, help='Number of leftmost 0 bits')
args = parser.parse_args()

sqs = boto3.resource('sqs', region_name='us-east-2')
queue = sqs.get_queue_by_name(QueueName='cnd_queue.fifo')

# d_val = 28

# Push messages onto queue
queue.send_message(
    MessageBody='NonceRequest_' + str(random.randint(1, 1000)),
    MessageAttributes={
        'StartValue': {
            'StringValue': '0',
            'DataType': 'String'
        },
        'EndValue': {
            'StringValue': '4294967296',
            'DataType': 'String'
        },
        'DValue': {
            'StringValue': str(args.d_val),
            'DataType': 'String'
        }
    },
    MessageGroupId='cnd'
)
