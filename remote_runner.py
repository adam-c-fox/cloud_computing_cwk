import boto3
import os
import time
import argparse

parser = argparse.ArgumentParser(description="Let's go Nonce hunting in the cloud!")
parser.add_argument('d_val', metavar='D', type=int, help='Number of leftmost 0 bits')
parser.add_argument('num_machines', metavar='N', type=int, help='Number of remote machines to use')
args = parser.parse_args()

# Connect
ec2 = boto3.resource('ec2', region_name='us-east-2')
sqs = boto3.resource('sqs', region_name='us-east-2')
sqsClient = boto3.client('sqs', region_name='us-east-2')
queue = sqs.get_queue_by_name(QueueName='cnd_queue.fifo')
responseQueue = sqs.get_queue_by_name(QueueName='cnd_responses')

# Push messages onto queue
maxValue = 4294967296
incrementValue = maxValue//int(args.num_machines)

print("Push messages onto queue...")
for i in range(0, int(args.num_machines)):
    startValue = i*incrementValue
    endValue = startValue + incrementValue
    print(str(i) + " | " + str(startValue) + " | " + str(endValue))

    queue.send_message(
        MessageBody='NonceRequest_'+str(i),
        MessageAttributes={
            'StartValue': {
                'StringValue': str(startValue),
                'DataType': 'String'
            },
            'EndValue': {
                'StringValue': str(endValue),
                'DataType': 'String'
            },
            'DValue': {
                'StringValue': str(args.d_val),
                'DataType': 'String'
            }
        },
        MessageGroupId='cnd'
    )

# Create UserData payload
user_data = '''#!/bin/bash
su ec2-user -c "nohup python3 /home/ec2-user/CND.py &"'''

# Create instances
print("Creating instances...")
instances = ec2.create_instances(ImageId='ami-0391e9e19d3ed0ca3',
                                 InstanceType='t2.micro',
                                 MinCount=1,
                                 MaxCount=int(args.num_machines),
                                 KeyName="AWSKeyPair1",
                                 UserData=user_data)

# Wait for message on cnd_responses queue
response = []
while('Messages' not in response):
    print("Waiting for response...")
    response = sqsClient.receive_message(
        QueueUrl=responseQueue.url,
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        WaitTimeSeconds=20
    )

# Delete message from queue
message = response['Messages'][0]
sqsClient.delete_message(
    QueueUrl=responseQueue.url,
    ReceiptHandle=message['ReceiptHandle']
)

print("NONCE: ")
print(message['MessageAttributes']['Nonce']['StringValue'])

# Terminate instances
print("Terminating instances...")
ids = []
for instance in instances:
    ids.append(instance.id)

ec2.instances.filter(InstanceIds=ids).terminate()

# Purge queues
sqsClient.purge_queue(QueueUrl=queue.url)
sqsClient.purge_queue(QueueUrl=responseQueue.url)
