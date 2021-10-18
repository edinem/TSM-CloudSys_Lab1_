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
