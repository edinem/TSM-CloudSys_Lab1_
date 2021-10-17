
"""
Name : aws_setup.py
Author : Edin Mujkanovic
Description : Script used to create automatically three instances on AWS to host a multi-tier application.
"""

import paramiko, boto3, time

key = None
instances_ips = []

def createSecurityGroup():
    ec2 = boto3.client('ec2')
    response = ec2.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')
    print("Creating Security Group...")
    try:
        response = ec2.create_security_group(GroupName='SecGroup',
                                             Description='General Security Group',
                                             VpcId=vpc_id)
        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))
        data = ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                 'FromPort': 8080,  # allows incoming traffic port 80
                 'ToPort': 8080,  # Allows port forwarding to port 80
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},  # Ip ranges to be functional
                {'IpProtocol': 'tcp',  # protocol to be used
                 'FromPort': 22,  # Allow incoming traffic from port 22
                 'ToPort': 22,  # Allow traffic to be reached at port 22
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp',  # protocol to be used
                 'FromPort': 443,  # Allow incoming traffic from port 22
                 'ToPort': 443,  # Allow traffic to be reached at port 22
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp',  # protocol to be used
                 'FromPort': 3306,  # Allow incoming traffic from port 22
                 'ToPort': 3306,  # Allow traffic to be reached at port 22
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ])
        print("Security Group Created")

    except Exception as e:
        print("Security Group already exists, skipping...")

def createDatabaseInstance():
    print("Creating Database EC2 Instance...")
    ec2 = boto3.resource("ec2")

    ec2.create_instances(
        ImageId='ami-02e136e904f3da870', # Image : Amazon Linux 2 AMI (HVM), SSD Volume Type
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName="cloud",
        SecurityGroups=[
            "SecGroup"
        ]
    )

def configureDatabaseInstance():
    global instances_ips
    global key

    print("Connecting to Database instance..")
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=instances_ips[0][1], username ="ec2-user", pkey=key)
    print("Uploading to Database instance..")
    ftp_client = ssh_client.open_sftp()
    ftp_client.put('./config_files/db/script.sh', 'script.sh')
    ftp_client.close()
    print("Executing the script on Database instance..")
    stdin, stdout, stderr = ssh_client.exec_command('bash script.sh')
    print(stdout.read())
    ssh_client.close()

def configureBackendInstance():
    global instances_ips
    global key

    print("Connecting to Backend instance..")
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=instances_ips[1][1], username ="ec2-user", pkey=key)
    print("Uploading to Backend instance..")
    ftp_client = ssh_client.open_sftp()
    ftp_client.put('./config_files/backend/script.sh', 'script.sh')
    ftp_client.close()
    print("Executing the script on Backend instance..")
    stdin, stdout, stderr = ssh_client.exec_command('bash script.sh')
    print(stdout.read())
    ssh_client.close()

def configureFrontendInstance():
    global instances_ips
    global key

    print("Connecting to Frontend instance..")
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=instances_ips[2][1], username ="ec2-user", pkey=key)
    print("Uploading to Frontend instance..")
    ftp_client = ssh_client.open_sftp()
    ftp_client.put('./config_files/frontend/script.sh', 'script.sh')
    ftp_client.close()
    print("Executing the script on Frontend instance..")
    stdin, stdout, stderr = ssh_client.exec_command('bash script.sh')
    print(stdout.read())
    ssh_client.close()



def createBackendInstance():
    print("Creating Backend EC2 Instance...")
    ec2 = boto3.resource("ec2")

    ec2.create_instances(
        ImageId='ami-02e136e904f3da870', # Image : Amazon Linux 2 AMI (HVM), SSD Volume Type
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName="cloud",
        SecurityGroups=[
            "SecGroup"
        ]
    )


def createFrontendInstance():
    print("Creating Frontend EC2 Instance...")
    ec2 = boto3.resource("ec2")

    ec2.create_instances(
        ImageId='ami-02e136e904f3da870', # Image : Amazon Linux 2 AMI (HVM), SSD Volume Type
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName="cloud",
        SecurityGroups=[
            "SecGroup"
        ]
    )

def getInstancesIP():
    global instances_ips
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(Filters=[{
        'Name': 'instance-state-name',
        'Values': ['running']}])
    for instance in instances:
        instances_ips.append([instance.private_ip_address, instance.public_ip_address])

    print(instances_ips)

def generateConfigScripts():
    global instances_ips
    print("Generating Database config script...")
    db_config_template = open('./config_files/db/script_template.sh', 'rt')
    db_config_output = open('./config_files/db/script.sh', 'wt')
    for line in db_config_template:
        db_config_output.write(line.replace('mysql_bind_address=""','mysql_bind_address="'+instances_ips[0][1]+'"\n' ))

    db_config_output.close()
    db_config_template.close()



    print("Generating Backend config script...")
    backend_config_template = open('./config_files/backend/script_template.sh', 'rt')
    backend_config_output = open('./config_files/backend/script.sh', 'wt')
    for line in backend_config_template:
        backend_config_output.write(line.replace('demo_app_mysql_server=""','demo_app_mysql_server="'+instances_ips[0][1]+'"\n' ))

    backend_config_output.close()
    backend_config_template.close()



    print("Generating Frontend config script...")
    frontend_config_template = open('./config_files/frontend/script_template.sh', 'rt')
    frontend_config_output = open('./config_files/frontend/script.sh', 'wt')
    for line in frontend_config_template:
        frontend_config_output.write(line.replace('web_server_name=""','web_server_name="'+instances_ips[2][1]+'"\n')
                                     .replace('app_server_name=""','app_server_name="'+instances_ips[1][1]+'"\n'))

    frontend_config_output.close()
    frontend_config_template.close()

    print("Config files generated ")





def main():
    global key
    global instances_ips
    key = paramiko.RSAKey.from_private_key_file("./cloud.pem")
    createSecurityGroup()
    createDatabaseInstance()
    createBackendInstance()
    createFrontendInstance()
    print("Instances created successfully...")
    print("Waiting 60 secondes before starting the configuration...")
    time.sleep(60)
    getInstancesIP()
    generateConfigScripts()

    configureDatabaseInstance()
    configureBackendInstance()
    configureFrontendInstance()

    print("Setting up the server has finished... you can access it via : https://"+instances_ips[2][1])




if __name__ == "__main__":
    main()