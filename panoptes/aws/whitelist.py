""" Panoptes - AWS - Whitelist

Generates the dynamic whitelist of AWS Resources, considering them not harmful
and known resources
"""

import concurrent.futures


def list_all_safe_ips(aws_client):
    """
    Function responsible for aggregating all methods and removing duplicates
    """
    list_all_safe_ips = []
    whitelisted_resources = {
        "vpc": get_vpc_ranges,
        "subnet": get_subnet_ranges,
        "instance_ips": get_vpc_instance_ips,
        "elastic_ips": get_elastic_ips
    }

    for aws_resource, get_function in whitelisted_resources.items():
        list_all_safe_ips += get_function(aws_client)

    return list(set(list_all_safe_ips))

def get_vpc_ranges(aws_client):
    """
    List VPCs CIDR ranges in the account
    """
    ec2 = aws_client.client('ec2')
    boto_vpcs = ec2.describe_vpcs()
    vpc_ranges = [
        vpc['CidrBlock'] for vpc in boto_vpcs['Vpcs']
    ]
    return list(set(vpc_ranges))


def get_subnet_ranges(aws_client):
    """
    List Subnets CIDR ranges in the account
    """
    ec2 = aws_client.client('ec2')
    boto_subnets = ec2.describe_subnets()
    subnet_ranges = [
        subnet['CidrBlock'] for subnet in boto_subnets['Subnets']
    ]
    return list(set(subnet_ranges))


def get_vpc_instance_ips(aws_client):
    """
    List Public and Private IPs from EC2 instances inside a VPC in the
    account
    """
    ec2 = aws_client.client('ec2')
    boto_instances = ec2.describe_instances()
    vpc_instances_ips = []
    for instance_obj in boto_instances['Reservations']:
        for instance in instance_obj['Instances']:
            for instance_net in instance['NetworkInterfaces']:
                if 'Association' in instance_net.keys():
                    vpc_instances_ips.append(
                        instance_net['Association']['PublicIp'] + '/32'
                    )
                if 'PrivateIpAddress' in instance_net.keys():
                    vpc_instances_ips.append(
                        instance_net['PrivateIpAddress'] + '/32'
                    )
                if 'PrivateIpAddresses' in instance_net.keys():
                    for priv_ip in instance_net['PrivateIpAddresses']:
                        if 'Association' in priv_ip.keys():
                            vpc_instances_ips.append(
                                priv_ip['Association']['PublicIp'] + '/32'
                            )
                        if 'PrivateIpAddress' in priv_ip.keys():
                            vpc_instances_ips.append(
                                priv_ip['PrivateIpAddress'] + '/32'
                            )
    return list(set(vpc_instances_ips))


def get_elastic_ips(aws_client):
    """
    List all Elastic IPs reserved in the account
    """
    ec2 = aws_client.client('ec2')
    boto_elastic_ips = ec2.describe_addresses()
    elastic_ips = []
    for elastic_ip in boto_elastic_ips['Addresses']:
        if 'PrivateIpAddress' in elastic_ip.keys():
            elastic_ips.append(
                elastic_ip['PrivateIpAddress'] + '/32'
            )
        elastic_ips.append(
            elastic_ip['PublicIp'] + '/32'
        )
    return list(set(elastic_ips))


if __name__ == "__main__":
    pass
