In this project i have used python based script to automate the creation and launching of ec2 instance from one region to another (in this case: Ireland region to singapore region)

1. Create the ami in ireland region.
2. Copy the ami in the target region.
3. Launch the instance in the target region rgion. (In my case singapore).

Note: As we know that if the volumes are encrypted by KMS we cannot copy the ami easily. for that we have created a KMS key beforehand in the target region.
