import boto3
import argparse
import math
import time

# Start Timing
begin = time.time()

# System runtime for a single machine (minutes)
runtime = 320

parser = argparse.ArgumentParser(description="Let's go Nonce hunting in the cloud!")
parser.add_argument('-d', action="store", dest="d_val", metavar='D', type=int, help='Number of leftmost 0 bits')
parser.add_argument('-n', action="store", dest="num_machines", metavar='N', type=int, help='Number of remote machines to use')
parser.add_argument('-t', action="store", dest="desired_runtime", metavar='N', type=int, help='Desired runtime in minutes')
parser.add_argument('-c', action="store", dest="confidence_level", metavar='C', type=float, help='Confidence level for runtime, between 0 and 1')
parser.add_argument('-timeout', action="store", dest="timeout", metavar='TO', type=float, help='Runtime timeout, secs')
args = parser.parse_args()

# Calculate number of machines, when given time
if (args.desired_runtime is not None and args.confidence_level is not None):
    num_machines = math.ceil(runtime/args.desired_runtime)
    num_machines = int(num_machines * args.confidence_level)
    print("Desired runtime of: " + str(args.desired_runtime) + " with confidence level: " + str(args.confidence_level))
    print("Required number of machines: " + str(num_machines))
else:
    num_machines = args.num_machines

# Connect
ec2 = boto3.resource('ec2', region_name='us-east-2')
sqs = boto3.resource('sqs', region_name='us-east-2')
sqsClient = boto3.client('sqs', region_name='us-east-2')
queue = sqs.get_queue_by_name(QueueName='cnd_queue.fifo')
responseQueue = sqs.get_queue_by_name(QueueName='cnd_responses')

# Push messages onto queue
maxValue = 4294967296
incrementValue = maxValue//int(num_machines)

print("Push messages onto queue...")
for i in range(0, int(num_machines)):
    startValue = i*incrementValue
    endValue = startValue + incrementValue

    if i == int(num_machines)-1:
        endValue += (maxValue-endValue)

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
                                 MaxCount=int(num_machines),
                                 KeyName="AWSKeyPair1",
                                 UserData=user_data,
                                 CreditSpecification={
                                    'CpuCredits': 'unlimited'
                                 })

# Wait for message on cnd_responses queue
response = []
success = False
timeout = False
failCount = 0
while(not timeout and not success and failCount < int(num_machines)):
    while(not timeout and 'Messages' not in response):
        print("Waiting for response...")
        response = sqsClient.receive_message(
            QueueUrl=responseQueue.url,
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            WaitTimeSeconds=20
        )
        # Timeout check
        if(args.timeout is not None):
            timeout_test = time.time()
            check = timeout_test - begin
            if(check > int(args.timeout)):
                timeout = True
                break;

    if not timeout:
        message = response['Messages'][0]
        if(int(message['MessageAttributes']['Nonce']['StringValue']) == 0
        and int(message['MessageAttributes']['Binary']['StringValue']) == 0):
            failCount += 1
        else:
            success = True

        # Delete message from queue
        sqsClient.delete_message(
            QueueUrl=responseQueue.url,
            ReceiptHandle=message['ReceiptHandle']
        )
        time.sleep(2)
        response=[]



# End timing
termination = time.time()
elapsed_time = termination - begin

if(success):
    print("Golden Nonce Located...")
    print(message['MessageAttributes']['Nonce']['StringValue'])
    print(message['MessageAttributes']['Binary']['StringValue'])
    print('%.10f' % elapsed_time + ' secs')
else:
    print("No Golden Nonces Located...")

# Terminate instances
print("Terminating instances...")
ids = []
for instance in instances:
    ids.append(instance.id)

ec2.instances.filter(InstanceIds=ids).terminate()

# Purge queues
sqsClient.purge_queue(QueueUrl=queue.url)
sqsClient.purge_queue(QueueUrl=responseQueue.url)
