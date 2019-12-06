import boto3
import time

# Connect
ec2 = boto3.resource('ec2', region_name='us-east-2')

# Create instances
for x in range(0, 10):
    begin = time.time()
    instances = ec2.create_instances(ImageId='ami-0391e9e19d3ed0ca3',
                                     InstanceType='t2.micro',
                                     MinCount=1,
                                     MaxCount=1,
                                     KeyName="AWSKeyPair1")

    instance = instances[0]
    instance.wait_until_running()

    termination = time.time()
    elapsed_time = termination - begin
    print('%.10f' % elapsed_time + ' secs')

    # Terminate instances
    ids = []
    for instance in instances:
        ids.append(instance.id)

    ec2.instances.filter(InstanceIds=ids).terminate()
