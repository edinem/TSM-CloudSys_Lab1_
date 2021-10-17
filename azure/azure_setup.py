"""
Name : azure_setup.py
Author : Samuel Mettler
Description : Script used to create automatically three instances on AWS to host a multi-tier application.
Sources : Used various source from docs.microsoft.com/en-us/azure/developer
"""

# Import the needed credential and management objects from the libraries.
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
import os, time, paramiko


VNET_NAME = "labo1-vnet"
SUBNET_NAME = "labo1-subnet"
IP_NAME = ["labo1-ip-db", "labo1-ip-back", "labo1-ip-front"]
IP_CONFIG_NAME = "labo1-ip-config"
NIC_NAME = ["labo1-nic-db", "labo1-nic-back", "labo1-nic-front"]
RESOURCE_GROUP_NAME = "labo1"
LOCATION = "westeurope"
INSTANCE_IPS = []
# Acquire a credential object using CLI-based authentication.
credential = AzureCliCredential()

# Retrieve subscription ID from environment variable.
# subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
subscription_id = "86b1617d-af52-4f9c-b0ac-45b461d2281c"

def createNetworkSubnet():
    print("Creating network subnet")
    # Step 1: Provision a resource group

    #   Obtain the management object for resources, using the credentials from the CLI login.
    resource_client = ResourceManagementClient(credential, subscription_id)

    # Constants we need in multiple places: the resource group name and the region
    # in which we provision resources. You can change these values however you want.
    
    # Provision the resource group.
    rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME,
        {
            "location": LOCATION
        }
    )

    print(f"Provisioned resource group {rg_result.name} in the {rg_result.location} region")

    # Step 2: provision a virtual network
    # Obtain the management object for networks
    network_client = NetworkManagementClient(credential, subscription_id)
    
    # Provision the virtual network and wait for completion
    poller = network_client.virtual_networks.begin_create_or_update(RESOURCE_GROUP_NAME,
        VNET_NAME,
        {
            "location": LOCATION,
            "address_space": {
                "address_prefixes": ["10.0.0.0/16"]
            }
        }
    )
    network_client.virtual_networks.get(RESOURCE_GROUP_NAME, VNET_NAME)
    vnet_result = poller.result()

    print(f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}")

    poller = network_client.subnets.begin_create_or_update(RESOURCE_GROUP_NAME, 
    VNET_NAME, SUBNET_NAME,
    { "address_prefix": "10.0.0.0/24" }
    )
    subnet_result = poller.result()
    print(f"Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")

    


def createVM(VMName, network_client, NIC, IPName) :
    print(f"Provisioning a virtual machine...some operations might take a minute or two.")

    # Step 3: Provision the subnet and wait for completion
    poller = network_client.subnets.get(RESOURCE_GROUP_NAME, VNET_NAME, SUBNET_NAME)
    subnet_result = poller
    
    # Step 4: Provision an IP address and wait for completion
    poller = network_client.public_ip_addresses.begin_create_or_update(RESOURCE_GROUP_NAME,
        IPName,
        {
            "location": LOCATION,
            "sku": { "name": "Standard" },
            "public_ip_allocation_method": "Static",
            "public_ip_address_version" : "IPV4"
        }
    )

    ip_address_result = poller.result()

    print(f"Provisioned public IP address {ip_address_result.name} with address {ip_address_result.ip_address}")
    
    INSTANCE_IPS.append(ip_address_result.ip_address)
    # Step 5: Provision the network interface client
    poller = network_client.network_interfaces.begin_create_or_update(RESOURCE_GROUP_NAME,
        NIC, 
        {
            "location": LOCATION,
            "ip_configurations": [ {
                "name": IP_CONFIG_NAME,
                "subnet": { "id": subnet_result.id },
                "public_ip_address": {"id": ip_address_result.id }
            }]
        }
    )
    nic_result = poller.result()
   
    print(f"Provisioned network interface client {nic_result.name}")

    # Step 6: Provision the virtual machine

    # Obtain the management object for virtual machines
    compute_client = ComputeManagementClient(credential, subscription_id)

    VM_NAME = VMName
    USERNAME = "azureuser"
    PASSWORD = "ChangePa$$w0rd24"

    print(f"Provisioning virtual machine {VM_NAME}; this operation might take a few minutes.")

    # Provision the VM specifying only minimal arguments, which defaults to an Ubuntu 18.04 VM
    # on a Standard DS1 v2 plan with a public IP address and a default virtual network/subnet.

    poller = compute_client.virtual_machines.begin_create_or_update(RESOURCE_GROUP_NAME, VM_NAME,
        {
            "location": LOCATION,
            "storage_profile": {
                "image_reference": {
                    "publisher": 'OpenLogic',
                    "offer": "CentOS",
                    "sku": "7.5",
                    "version": "latest"
                }
            },
            "hardware_profile": {
                "vm_size": "Standard_DS1_v2"
            },
            "os_profile": {
                "computer_name": VM_NAME,
                "admin_username": USERNAME,
                "admin_password": PASSWORD
            },
            "network_profile": {
                "network_interfaces": [{
                    "id": nic_result.id,
                }]
            }        
        }
    )

    vm_result = poller.result()

    print(f"Provisioned virtual machine {vm_result.name}")

def createFrontendInstance(network_client):
    print("\nConfiguring Front\n")
    createVM("Front", network_client, NIC_NAME[2], IP_NAME[2])

def createDatabaseInstance(network_client):
    print("\nConfiguring Database\n")

    createVM("Database", network_client, NIC_NAME[0], IP_NAME[0])

def createBackendInstance(network_client):
    print("\nConfiguring Backend\n")

    createVM("Back", network_client, NIC_NAME[1], IP_NAME[1])

def generateConfigScripts():

    print("Generating Database config script...")
    db_config_template = open('./config_files/db/script_template.sh', 'rt')
    db_config_output = open('./config_files/db/script.sh', 'wt')
    for line in db_config_template:
        db_config_output.write(line.replace('mysql_bind_address=""','mysql_bind_address="'+INSTANCE_IPS[0]+'"\n' ))

    db_config_output.close()
    db_config_template.close()

    print("Generating Backend config script...")
    backend_config_template = open('./config_files/backend/script_template.sh', 'rt')
    backend_config_output = open('./config_files/backend/script.sh', 'wt')
    for line in backend_config_template:
        backend_config_output.write(line.replace('demo_app_mysql_server=""','demo_app_mysql_server="'+INSTANCE_IPS[1]+'"\n' ))

    backend_config_output.close()
    backend_config_template.close()



    print("Generating Frontend config script...")
    frontend_config_template = open('./config_files/frontend/script_template.sh', 'rt')
    frontend_config_output = open('./config_files/frontend/script.sh', 'wt')
    for line in frontend_config_template:
        frontend_config_output.write(line.replace('web_server_name=""','web_server_name="'+INSTANCE_IPS[2] +'"\n')
                                     .replace('app_server_name=""','app_server_name="'+INSTANCE_IPS[1]+'"\n'))

    frontend_config_output.close()
    frontend_config_template.close()

    print("Config files generated ")


def configureDatabaseInstance():

    print("Connecting to Database instance..")
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=INSTANCE_IPS[0], username ="azureuser", pkey=key)
    print("Uploading to Database instance..")
    ftp_client = ssh_client.open_sftp()
    ftp_client.put('./config_files/db/script.sh', 'script.sh')
    ftp_client.close()
    print("Executing the script on Database instance..")
    stdin, stdout, stderr = ssh_client.exec_command('bash script.sh')
    print(stdout.read())
    ssh_client.close()

def configureBackendInstance():

    print("Connecting to Backend instance..")
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=INSTANCE_IPS[1], username ="azureuser", pkey=key)
    print("Uploading to Backend instance..")
    ftp_client = ssh_client.open_sftp()
    ftp_client.put('./config_files/backend/script.sh', 'script.sh')
    ftp_client.close()
    print("Executing the script on Backend instance..")
    stdin, stdout, stderr = ssh_client.exec_command('bash script.sh')
    print(stdout.read())
    ssh_client.close()

def configureFrontendInstance():

    print("Connecting to Frontend instance..")
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=INSTANCE_IPS[2], username ="azureuser", pkey=key)
    print("Uploading to Frontend instance..")
    ftp_client = ssh_client.open_sftp()
    ftp_client.put('./config_files/frontend/script.sh', 'script.sh')
    ftp_client.close()
    print("Executing the script on Frontend instance..")
    stdin, stdout, stderr = ssh_client.exec_command('bash script.sh')
    print(stdout.read())
    ssh_client.close()


def main():
    global key
    global VNET_NAME 
    global SUBNET_NAME 
    global IP_NAME 
    global IP_CONFIG_NAME 
    global NIC_NAME
    global RESOURCE_GROUP_NAME
    global LOCATION

    global INSTANCE_IPS

    network_client = NetworkManagementClient(credential, subscription_id)
    key = paramiko.RSAKey.from_private_key_file("./azureuser.pem")

    #createNetworkSubnet()

    #createDatabaseInstance(network_client)
    #createBackendInstance(network_client)
    #createFrontendInstance(network_client)

    print("Instances created successfully...")
    print("Waiting 60 secondes before starting the configuration...")
    #time.sleep(60)

    INSTANCE_IPS = ['13.81.253.241', '13.73.140.135', '13.81.6.140']
    generateConfigScripts()

    configureDatabaseInstance()
    configureBackendInstance()
    configureFrontendInstance()

    print("Setting up the server has finished... you can access it via : https://"+INSTANCE_IPS[2])

if __name__ == "__main__" :
    main()