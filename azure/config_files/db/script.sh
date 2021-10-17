#!/bin/bash
# Install the database
sudo tee /etc/yum.repos.d/mariadb.repo<<EOF
[mariadb]
name = MariaDB
baseurl = http://yum.mariadb.org/10.5/centos7-amd64
gpgkey=https://yum.mariadb.org/RPM-GPG-KEY-MariaDB
gpgcheck=1
EOF
sudo yum makecache 
sudo yum install MariaDB-server MariaDB-client -y
sudo systemctl enable --now mariadb



## Configure the Database
mysql_user_name='cloud_user'
mysql_user_password='#Welcome123'
mysql_root_password='#Welcome123'
mysql_app_database='cloudapp'
mysql_bind_address="20.101.89.227"

# Secure the database installation
sudo /usr/bin/mysqladmin -u root password "$mysql_root_password"
sudo /usr/bin/mysql -u root -p"$mysql_root_password" -e "SET PASSWORD FOR 'root'@localhost = PASSWORD('$mysql_root_password')"
/usr/bin/mysql -u root -p"$mysql_root_password" -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1')"
/usr/bin/mysql -u root -p"$mysql_root_password" -e "DELETE FROM mysql.user WHERE User=''"
/usr/bin/mysql -u root -p"$mysql_root_password" -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\_%'"
# Add the app user and database
/usr/bin/mysql -u root -p"$mysql_root_password" -e "CREATE DATABASE $mysql_app_database;"
/usr/bin/mysql -u root -p"$mysql_root_password" -e "GRANT ALL PRIVILEGES ON $mysql_app_database.* TO '$mysql_user_name'@'%' IDENTIFIED BY '$mysql_user_password';"
# Flush privileges
/usr/bin/mysql -u root -p"$mysql_root_password" -e "FLUSH PRIVILEGES"
# Enable remote connections
/usr/bin/echo "bind-address = $mysql_bind_address" >> sudo tee -a /etc/my.cnf
# Open MySQL firewall for remote connections
sudo systemctl restart mariadb