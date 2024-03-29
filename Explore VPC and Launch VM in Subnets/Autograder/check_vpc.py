import boto3
import json

def check_vpc_and_subnets(region, access_key, secret_key):
    ec2 = boto3.resource('ec2', region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)

    for vpc in ec2.vpcs.all():
        if vpc.tags is None:
            continue
        for tag in vpc.tags:
            if 'Name' in tag['Key'] and tag['Value'] == 'aws-vpc':
                if vpc.cidr_block == '10.1.0.0/16':
                    print(f"VPC {vpc.id} with name {tag['Value']} and CIDR block {vpc.cidr_block} is created correctly.")
                else:
                    print(f"VPC {vpc.id} with name {tag['Value']} does not have the correct CIDR block.")
                for subnet in vpc.subnets.all():
                    if subnet.tags is None:
                        continue
                    for tag in subnet.tags:
                        if 'Name' in tag['Key']:
                            if tag['Value'] == 'subnet-public-a':
                                if subnet.map_public_ip_on_launch and subnet.cidr_block == '10.1.1.0/24':
                                    print(f"Public subnet {subnet.id} with name {tag['Value']} and CIDR block {subnet.cidr_block} is created correctly.")
                                else:
                                    print(f"Public subnet {subnet.id} with name {tag['Value']} is not correctly configured.")
                            elif tag['Value'] == 'subnet-public-b':
                                if subnet.map_public_ip_on_launch and subnet.cidr_block == '10.1.2.0/24':
                                    print(f"Public subnet {subnet.id} with name {tag['Value']} and CIDR block {subnet.cidr_block} is created correctly.")
                                else:
                                    print(f"Public subnet {subnet.id} with name {tag['Value']} is not correctly configured.")
                            elif tag['Value'] == 'subnet-private-a':
                                if not subnet.map_public_ip_on_launch and subnet.cidr_block == '10.1.3.0/24':
                                    print(f"Private subnet {subnet.id} with name {tag['Value']} and CIDR block {subnet.cidr_block} is created correctly.")
                                else:
                                    print(f"Private subnet {subnet.id} with name {tag['Value']} is not correctly configured.")
                            elif tag['Value'] == 'subnet-private-b':
                                if not subnet.map_public_ip_on_launch and subnet.cidr_block == '10.1.4.0/24':
                                    print(f"Private subnet {subnet.id} with name {tag['Value']} and CIDR block {subnet.cidr_block} is created correctly.")
                                else:
                                    print(f"Private subnet {subnet.id} with name {tag['Value']} is not correctly configured.")

# Load data from file
with open('iam.txt', 'r') as f:
    data = json.load(f)

check_vpc_and_subnets(data['region_name'], data['aws_access_key_id'], data['aws_secret_access_key'])
