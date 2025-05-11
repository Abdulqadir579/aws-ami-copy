import boto3
import time

SOURCE_REGION = 'eu-west-1'
TARGET_REGION = 'ap-southeast-1'
INSTANCE_ID = 'i-05beba26995de5dd2'
TARGET_KMS_KEY_ID = 'arn:aws:kms:ap-southeast-1:340752808710:key/5cc7ad26-570f-4c2b-9921-487fd81f049e'


# Initialize clients
ec2_src = boto3.client('ec2', region_name=SOURCE_REGION)
ec2_dst = boto3.client('ec2', region_name=TARGET_REGION)

# 1. Create an AMI from the source instance
ami_name = f"ami-migration-{INSTANCE_ID}-{int(time.time())}"
print(f"Creating AMI please hold for a moment: {ami_name}")
ami_response = ec2_src.create_image(InstanceId=INSTANCE_ID, Name=ami_name, NoReboot=True)
source_ami_id = ami_response['ImageId']

# Wait for the AMI to be available
print("Waiting for AMI to become available...")
waiter = ec2_src.get_waiter('image_available')
waiter.wait(ImageIds=[source_ami_id])
print(f"AMI {source_ami_id} is now available.")

# 2. Copy the AMI to the target region with encryption
print(f"Copying AMI to {TARGET_REGION} with encryption")
copy_response = ec2_dst.copy_image(
    Name=ami_name,
    SourceImageId=source_ami_id,
    SourceRegion=SOURCE_REGION,
    Encrypted=True,
    KmsKeyId=TARGET_KMS_KEY_ID
)
copied_ami_id = copy_response['ImageId']

# Wait for the copied AMI to be available
print("Waiting for copied AMI to become available in target region...")
waiter_dst = ec2_dst.get_waiter('image_available')
waiter_dst.wait(ImageIds=[copied_ami_id])
print(f"Copied AMI {copied_ami_id} is available in {TARGET_REGION}.")

# 3. Launch EC2 from copied AMI (optional - example only)
print("Launching new EC2 instance from copied AMI...")
instance_response = ec2_dst.run_instances(
    ImageId=copied_ami_id,
    InstanceType='t2.micro',
    MinCount=1,
    MaxCount=1,
    KeyName='ireland',
    SubnetId='subnet-07431559e1c3cc2cb',
    SecurityGroupIds=['sg-03e6ec8771a145a3b'],
)
print("Instance launched:", instance_response['Instances'][0]['InstanceId'])

