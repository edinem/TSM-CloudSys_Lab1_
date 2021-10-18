
#!/usr/bin/env python

# Source : https://cloud.google.com/compute/docs/tutorials/python-guide
#          https://choshicure.hatenablog.com/entry/gcp-china-denied
# Auteur : Victor Truan


import time
import paramiko, time
import googleapiclient.discovery
from six.moves import input

def list_instances():
    global compute
    global project_id
    global zone
    result = compute.instances().list(project=project_id, zone=zone).execute()
    return result['items'] if 'items' in result else None

def delete_instance(name):
    global compute
    global project_id
    global zone
    return compute.instances().delete(
        project=project_id,
        zone=zone,
        instance=name).execute()

def wait_for_operation(compute, project, zone, operation):
    print('Waiting for operation to finish...')
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)

def createInstance(name):
    print("Creating "+name+" GCE Instance...")
    # Get the latest Debian Jessie image.
    image_response = compute.images().getFromFamily(project='centos-cloud', family='centos-7').execute()
    source_disk_image = image_response['selfLink']
    startup_script = open('./config_files/'+name+'/script.sh', 'r').read()
    # Configure the machine
    machine_type = "zones/%s/machineTypes/n1-standard-1" % zone
    config = {
        'name': name,
        'machineType': machine_type,
        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],
        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [
        {
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],
        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],
        'metadata': {
            'items': [{
                # Startup script is automatically executed by the
                # instance upon startup.
                'key': 'startup-script',
                'value': startup_script
            }]
        }
    }
    operation =  compute.instances().insert(project=project_id, zone=zone, body=config).execute()
    wait_for_operation(compute, project_id, zone, operation['name'])

def createAndConfigureDatabaseInstance():
    createInstance("db")

def generateBackendScript():
    instances = list_instances()
    for instance in instances:
        if instance["name"] == "db":
            database_ip = instance['networkInterfaces'][0]['networkIP']
    print("Generating Backend config script...")
    backend_config_template = open('./config_files/backend/script_template.sh', 'rt')
    backend_config_output = open('./config_files/backend/script.sh', 'wt')
    for line in backend_config_template:
        backend_config_output.write(line.replace('demo_app_mysql_server=""','demo_app_mysql_server="'+database_ip+'"\n' ))
    backend_config_output.close()
    backend_config_template.close()

def createAndConfigureBackendInstance():
    createInstance("backend")

def createFrontendInstance():
    print("Creating Frontend GCE Instance...")
    # Get the latest Debian Jessie image.
    image_response = compute.images().getFromFamily(
        project='centos-cloud', family='centos-7').execute()
    source_disk_image = image_response['selfLink']
    # Configure the machine
    machine_type = "zones/%s/machineTypes/n1-standard-1" % zone
    config = {
        'name': "frontend",
        'machineType': machine_type,
        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],
        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [
        {
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],
        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }]
    }

    operation =  compute.instances().insert(project=project_id, zone=zone, body=config).execute()
    wait_for_operation(compute, project_id, zone, operation['name'])
    firewall_body={
        'name':"http",
        'allowed':[
            {
                "IPProtocol":'tcp',
                "ports":443
            },
            {
                "IPProtocol":'tcp',
                "ports":80
            },
            {
                "IPProtocol":'tcp',
                "ports":8080
            }],
        "sourceRanges": ['0.0.0.0/0']
    }
    request = compute.firewalls().insert(project=project_id, body=firewall_body)

def generateFrontendScript():
    instances = list_instances()
    for instance in instances:
        if instance["name"] == "backend":
            backend_ip = instance['networkInterfaces'][0]['networkIP']
        if instance["name"] == "frontend":
            frontend_ip = instance['networkInterfaces'][0]['accessConfigs'][0]['natIP']
    print("Generating Frontend config script...")
    frontend_config_template = open('./config_files/frontend/script_template.sh', 'rt')
    frontend_config_output = open('./config_files/frontend/script.sh', 'wt')
    for line in frontend_config_template:
        frontend_config_output.write(line.replace('web_server_name=""','web_server_name="'+frontend_ip+'"\n')
                                     .replace('app_server_name=""','app_server_name="'+backend_ip+'"\n'))

    frontend_config_output.close()
    frontend_config_template.close()

    print("Config files generated ")

def configureFrontendInstance():
    key = paramiko.RSAKey.from_private_key_file("./cloud.pem")
    instances = list_instances()
    for instance in instances:
        if instance["name"] == "frontend":
            frontend_ip = instance['networkInterfaces'][0]['accessConfigs'][0]['natIP']
    print("Connecting to Frontend instance..")
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=frontend_ip, username =username, pkey=key)
    print("Uploading to Frontend instance..")
    ftp_client = ssh_client.open_sftp()
    ftp_client.put('./config_files/frontend/script.sh', 'script.sh')
    ftp_client.close()
    print("Executing the script on Frontend instance..")
    stdin, stdout, stderr = ssh_client.exec_command('bash script.sh')
    print(stdout.read())
    print(stderr.read())
    ssh_client.close()

def main():
    global project_id
    project_id = 'the-bird-326707'
    global username
    username = 'vtruanheig'
    global zone
    zone = 'us-central1-f'
    global compute
    compute = googleapiclient.discovery.build('compute', 'v1')
    print("Creating database...")
    createAndConfigureDatabaseInstance()
    generateBackendScript()
    time.sleep(60)

    print("Creating backend...")
    createAndConfigureBackendInstance()

    print("Creating frontend...")
    createFrontendInstance()
    time.sleep(60)
    generateFrontendScript()
    configureFrontendInstance()    

    instances = list_instances()
    for instance in instances:
        if instance["name"] == "frontend":
            frontend_ip = instance['networkInterfaces'][0]['accessConfigs'][0]['natIP']
    print("Setting up the server has finished... you can access it via : https://"+frontend_ip)

if __name__ == "__main__":
    main()
