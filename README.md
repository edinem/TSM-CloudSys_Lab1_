# TSM-CloudSys_Lab1_
## Lab 1: Infrastructures as a Service, a comparative study
## Auteurs : Samuel Mettler, Victor Truan, Robin Cuenoud, Eric Emmanuel Zo’Oatcham et Edin Mujkanovic




## 1. AWS
### 1.1 Requirements
```
boto3, paramiko

pip3 install boto3 paramiko
```
Il faut également l'outil CLI aws d'installé et configuré.

#### 1.2 Comment lancer
Afin de lancer le script, il faut : 
- Configurer l'outil CLI AWS
- Aller dans le dossier `aws`
- Remplacer la clé `cloud.pem` par la votre tout en gardant le même nom.
- Lancer le script python `python3 aws_setup.py`
- Le script se lance. Il prend environ 5 minutes à s'exécuter.


## 2. Azure
### 2.1 Requirements

1. Il y a plusieurs requirement à installer :
```
sudo apt install azure-cli
sudo pip install -r requirements.txt
```

2. De plus, il faut _impérativement_ changer le `subscription_id` avec votre valeur obtenue lors de l'authentification avec Azure CLI.
Plus de détail ici : [Setup Azure environment](https://docs.microsoft.com/en-us/azure/developer/python/configure-local-development-environment?tabs=cmd)

3. Afin de pouvoir se connecter en SSH au VM, il faut créer une clef SSH et la mettre sur Azure. Sur linux, la commande est : `ssh-keygen -t rsa -C azureuser`. Le fichier utilisé pour stocker la clef privée est : `azurelab.pem` et doit être présent dans le répertoire `/azure`
Sans ceci, les scripts de configuration des machines ne seront pas déployé.

### 2.2 Utilisation

Dans le dossier d'azure :
`python3 azure_setup.py`
Le script se lance et après environ 6-7 minutes tout devrait fonctionner et vous pourrez vous connectez à l'API avec l'IP écrite à la fin du script.

## 3. Google Cloud Engine
### 3.1 Requirements

1. Il existe un fichier requirements.txt qu'il faut installer :
```
sudo pip install -r requirements.txt
```

2. Depuis le Google Cloud Engine bashboard il est nécessaire de créer un projet afin de se voir attribué un Id de projet.
Plus de détail ici : [Google Cloud Engine bashboard](https://console.cloud.google.com/home/dashboard)

3. De plus, il faut _impérativement_ changer la variable `project_id` avec l'ID de votre projet Google Cloud Engine disponible sur votre tableau de bord. Cette variable est diaponible dans le `main` du script `gce_script.py`

4. Afin de pouvoir se connecter en SSH au VM, il faut créer une clef SSH et la mettre sur Azure. Sur linux, la commande est : `ssh-keygen -t rsa -f ./cloud.pem -C [NomDuCompteGoogle]`. Le nom de compte est le String qui précéde le @ de votre compte. Le fichier utilisé pour stocker la clef privée est : `cloud.pem` et doit être présent dans le répertoire `/gce`. Il est nécessaire de renseigner la clef publique liée a cette clef privée sur votre compte Google.
Plus de détail ici : [Google Cloud Engine gestion clef ssh](https://console.cloud.google.com/compute/metadata/sshKeys)
Sans ceci, les scripts de configuration des machines ne seront pas déployé.



### 3.2 Utilisation

Dans le dossier gce :
`python3 gce_script.py`
Le script se lance et après environ 5 minutes tout devrait fonctionner et vous pourrez vous connectez à l'API avec l'IP écrite à la fin du script.
