import boto3
ec2 = boto3.resource('ec2', region_name='us-east-2')

Output = open('AWSKeyPair1.pem', 'w')
KeyPair = ec2.create_key_pair(KeyName='AWSKeyPair1')
KeyPairOutput = str(KeyPair.key_material)
Output.write(KeyPairOutput)
