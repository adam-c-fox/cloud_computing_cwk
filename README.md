# cloud_computing_cwk
COMSM0010 - Cloud Computing - 'Golden Nonce' coursework

## Usage

```> python3 remote_runner.py -d 28 -n 8```

Runs the system with Difficulty Level 28, over 8 remote hosts

```> python3 remote_runner.py -d 28 -t 60 -n 0.8``` 

Runs the system with Difficulty Level 28, runtime within 60 minutes, at a confidence level of 80%

## Local Initialisation
To run the `remote_runner.py` local script, it is necessary to setup AWS credentials for Boto3. Your Access key and Secret Key can be found in the AWS dashboard, you can opt to either use the default IAM user or create a new one for this system. 

The recommended location storing AWS credentials for use with Boto3 is at `~/.aws/credentials`, with the following file format:

```
[default]
aws_access_key_id=foo
aws_secret_access_key=bar
```

## Remote Resource Creation
Inside the `/utils` directory we provide a CloudFormation JSON file for sepcifying the correct SQS queue structure. To create the queues (a one-time operation):

1. Navigate to AWS CloudFormation
2. Click "Create Stack"
3. Leave "Template is ready" selected, and choose "Upload a template file"
4. Upload `create_queues.json`
5. Click "Next"
6. Enter a stack name of your choosing, perhaps `CND`
7. Click "Next" through the subsequent forms
8. Finally, click "Create Stack"

This will initialise the queues correctly.


## AMI Image Creation
It is necessary to add these credentials to the remote machine image also. I have provided a template image containing: Python3, Boto3, and CND.py, but no credentials. 

Follow these steps to create your personalised image:

1. Locate the image with the id `ami-0cdc46a6bbb371a54`, it will be called CloudNonceDiscoveryTemplateImage
2. Launch an instance of this image, using a KeyPair you have access to
3. Once launched, SCP your local `~/.aws/credentials/` to the same location on the remote machine
4. Save this as a private personal image (Instances, right-click > Image > Create Image)
5. Change the `image-id` in `remote_runner.py` to reflect the one from step 4

This will allow your remote instances access to the SQS infrastructure we put in place previously.


## AWS Lambda
The `/lambda` directory provides a SAM file (`CloudNonceDiscovery.yaml`), which specifies the configuration of the Lambda function. And also provides a `lambda_function.py`, the function itself.

Following the instructions provided [here](https://docs.aws.amazon.com/codedeploy/latest/userguide/tutorial-lambda-sam.html), will allow you to create the Lambda function with YAML file, before adding the Python manually after creation.
