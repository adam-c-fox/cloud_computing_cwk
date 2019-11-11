import hashlib
import argparse
import time
import boto3

def sendResponse(nonce, binary, sqsClient, responseQueueUrl):
    response = sqsClient.send_message(
        QueueUrl=responseQueueUrl,
        MessageBody='NonceResponse',
        MessageAttributes={
            'Nonce': {
                'DataType': 'String',
                'StringValue': str(nonce)
            },
            'Binary': {
                'DataType': 'String',
                'StringValue': str(binary)
            }
        }
    )

parser = argparse.ArgumentParser(description="Let's go Nonce hunting!")
parser.add_argument('d_val', metavar='D', type=int, help='Number of leftmost 0 bits')
args = parser.parse_args()

block = 'COMSM0010cloud'
D = args.d_val

begin = time.time()

# Connect
sqs = boto3.resource('sqs', region_name='us-east-2')
queue = sqs.get_queue_by_name(QueueName='cnd_queue.fifo')
responseQueue = sqs.get_queue_by_name(QueueName='cnd_responses')

# Receive message
sqsClient = boto3.client('sqs', region_name='us-east-2')
response = sqsClient.receive_message(
    QueueUrl=queue.url,
    MaxNumberOfMessages=1,
    MessageAttributeNames=[
        'All'
    ]
)

# Parse message
message = response['Messages'][0]
startValue = message['MessageAttributes']['StartValue']['StringValue']
endValue =   message['MessageAttributes']['EndValue']['StringValue']
print("Message: " + startValue + " | " + endValue)

# Delete message from queue
sqsClient.delete_message(
    QueueUrl=queue.url,
    ReceiptHandle=message['ReceiptHandle']
)

for nonce in range(int(startValue), int(endValue)):
    blockandnonce = block.encode('utf-8') + nonce.to_bytes(4, byteorder='big')
    hashValue = hashlib.sha256(hashlib.sha256(blockandnonce).digest()).hexdigest()
    binary = bin(int(hashValue, 16))[2:].zfill(256)

    if(int(binary[0:D]) == 0):
        termination = time.time()
        elapsed_time = termination - begin
        print(nonce)
        print('%.10f' % elapsed_time + ' secs')
        sendResponse(nonce, binary, sqsClient, responseQueue.url)
        break
