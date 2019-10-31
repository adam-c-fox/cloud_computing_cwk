import boto3
import os
import time

# Connect
ec2 = boto3.resource('ec2', region_name='us-east-2')

# Create instances
instances = ec2.create_instances(ImageId='ami-00e9e85eb9ab5c284',
                                 InstanceType='t2.micro',
                                 MinCount=1,
                                 MaxCount=1,
                                 KeyName="AWSKeyPair1")

instance = instances[0]
print('Waiting until running...')
instance.wait_until_running()
print('Running...')

time.sleep(5)
instance.reload()

# Copy script to remote host
print("Copy script to remote host...")
os.system('scp -i keypairs/AWSKeyPair1.pem -o "StrictHostKeyChecking no" '+
          +' CND.py ec2-user@%s:~/' % (instance.public_dns_name))

# Run script on remote host
print("Run script on remote host...")
os.system('ssh -i keypairs/AWSKeyPair1.pem ec2-user@%s "python3 CND.py %d"' % (instance.public_dns_name, 11))

# Terminate instances
ids = [instance.id]
ec2.instances.filter(InstanceIds=ids).terminate()
