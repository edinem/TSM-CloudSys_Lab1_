#!/bin/bash
# Install Apache and PHP
sudo /usr/bin/yum -y install mysql httpd php php-mysqlnd php-common php-gd php-xml php-mbstring php-mcrypt php-xmlrpc unzip wget
# Download and install Demo app
sudo /usr/bin/wget -O /var/www/html/config.php https://raw.githubusercontent.com/sammcgeown/vRA-3-Tier-Application/master/app/config.php
sudo /usr/bin/wget -O /var/www/html/create.php https://raw.githubusercontent.com/sammcgeown/vRA-3-Tier-Application/master/app/create.php
sudo /usr/bin/wget -O /var/www/html/delete.php https://raw.githubusercontent.com/sammcgeown/vRA-3-Tier-Application/master/app/delete.php
sudo /usr/bin/wget -O /var/www/html/error.php https://raw.githubusercontent.com/sammcgeown/vRA-3-Tier-Application/master/app/error.php
sudo /usr/bin/wget -O /var/www/html/index.php https://raw.githubusercontent.com/sammcgeown/vRA-3-Tier-Application/master/app/index.php
sudo /usr/bin/wget -O /var/www/html/read.php https://raw.githubusercontent.com/sammcgeown/vRA-3-Tier-Application/master/app/read.php
sudo /usr/bin/wget -O /var/www/html/update.php https://raw.githubusercontent.com/sammcgeown/vRA-3-Tier-Application/master/app/update.php

mysql_user_name='cloud_user'
mysql_user_password='#Welcome123'
mysql_root_password='#Welcome123'
mysql_app_database='cloudapp'
demo_app_mysql_server=""
hostname='Cloud App'

sudo /usr/bin/sed -i "s@DBName@$mysql_app_database@" /var/www/html/config.php
sudo /usr/bin/sed -i "s@DBUser@$mysql_user_name@" /var/www/html/config.php
sudo /usr/bin/sed -i "s@DBPassword@$mysql_root_password@" /var/www/html/config.php
sudo /usr/bin/sed -i "s@DBServer@$demo_app_mysql_server@" /var/www/html/config.php
sudo /usr/bin/sed -i "s@HOSTNAME@$hostname@" /var/www/html/index.php
sudo /usr/bin/wget -O /tmp/employees.sql https://raw.githubusercontent.com/sammcgeown/vRA-3-Tier-Application/master/app/employees.sql
sudo /usr/bin/mysql -u "$mysql_user_name" -p"$mysql_root_password" cloudapp -h $demo_app_mysql_server < /tmp/employees.sql
# Configure and start Apache
sudo /usr/bin/sed -i "/^&lt;Directory \"\/var\/www\/html\"&gt;/,/^&lt;\/Directory&gt;/{s/AllowOverride None/AllowOverride All/g}" /etc/httpd/conf/httpd.conf
sudo /usr/bin/sed -i "s@Listen 80@Listen 8080@" /etc/httpd/conf/httpd.conf
sudo /usr/bin/systemctl enable httpd.service
sudo /usr/bin/systemctl start httpd.service
sudo setsebool -P httpd_can_network_connect 1