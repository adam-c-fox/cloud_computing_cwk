import boto3
import os

#Connect
ec2 = boto3.resource('ec2', region_name='us-east-2')

# Create instances
instances = ec2.create_instances(ImageId='ami-00c03f7f7f2ec15c3',
                                InstanceType='t2.micro',
                                MinCount=1,
                                MaxCount=1,
                                KeyName="AWSKeyPair1")

for instance in instances:
    print(instance.id, instance.instance_type)
    #print(instance.public_dns_name)
    #print(instance.public_ip_address)
    #os.system('scp -i ../awskey.pem CND.py ubuntu@%s:~/' % (instance.public_ip_address))
