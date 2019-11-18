import boto3
import os
import time
import argparse

parser = argparse.ArgumentParser(description="Let's go Nonce hunting in the cloud!")
parser.add_argument('d_val', metavar='D', type=int, help='Number of leftmost 0 bits')
args = parser.parse_args()

def WaitForAll(instances):
    allAlive = False
    noOfInstances = len(instances)

    while (not allAlive):
        count = 0;
        for instance in instances:
            instance.reload()
            if (instance.state['Name'] == "running"):
                count += 1

        if (count == noOfInstances):
            allAlive = True

        time.sleep(10)


# Connect
ec2 = boto3.resource('ec2', region_name='us-east-2')
sqs = boto3.resource('sqs', region_name='us-east-2')
sqsClient = boto3.client('sqs', region_name='us-east-2')
queue = sqs.get_queue_by_name(QueueName='cnd_queue.fifo')
responseQueue = sqs.get_queue_by_name(QueueName='cnd_responses')

# Create instances
instances = ec2.create_instances(ImageId='ami-00e9e85eb9ab5c284',
                                 InstanceType='t2.micro',
                                 MinCount=1,
                                 MaxCount=1,
                                 KeyName="AWSKeyPair1")

print('Waiting until running...')
WaitForAll(instances)
print('Running...')

# Push messages onto queue
queue.send_message(
    MessageBody='NonceRequest',
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

# Copy script to remote hosts
for instance in instances:
    print("Copy script to remote host: " + instance.public_dns_name)
    os.system('scp -i keypairs/AWSKeyPair1.pem -o "StrictHostKeyChecking no" CND.py ec2-user@%s:~/' % (instance.public_dns_name))

# Run script on remote hosts
for instance in instances:
    print("Run script on remote host: " + instance.public_dns_name)
    os.system('ssh -i keypairs/AWSKeyPair1.pem ec2-user@%s "nohup python3 CND.py &"' % (instance.public_dns_name))

# Wait for message on cnd_responses queue
response = sqsClient.receive_message(
    QueueUrl=responseQueue.url,
    MaxNumberOfMessages=1,
    MessageAttributeNames=[
        'All'
    ],
    WaitTimeSeconds = 3600
)

print(response)

# Terminate instances
ids = []
for instance in instances:
    ids.append(instance.id)

ec2.instances.filter(InstanceIds=ids).terminate()
