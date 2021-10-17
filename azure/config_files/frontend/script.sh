#!/bin/bash
# Add epel-release
sudo amazon-linux-extras install epel -y
# Install nginx
sudo yum install nginx -y
# Download the reverse proxy configuration
sudo /usr/bin/wget -O /etc/nginx/conf.d/proxy.conf https://raw.githubusercontent.com/sammcgeown/vRA-3-Tier-Application/master/config/proxy.nginx.conf
web_server_name="13.81.6.140"

app_server_name="13.73.140.135"

sudo /usr/bin/sed -i "s@SERVERNAME@$web_server_name@" /etc/nginx/conf.d/proxy.conf
sudo /usr/bin/sed -i "s@APPTIER@$app_server_name@" /etc/nginx/conf.d/proxy.conf
# Create the SSL folder
sudo /usr/bin/mkdir /etc/nginx/ssl
# Download the proxy SSL conf
sudo /usr/bin/wget -O /etc/nginx/ssl/proxy.conf https://raw.githubusercontent.com/sammcgeown/vRA-3-Tier-Application/master/config/proxy.ssl.conf
sudo /usr/bin/sed -i "s@WEBSERVERNAME@$web_server_name@" /etc/nginx/ssl/proxy.conf
# Generate SSL keys
sudo /usr/bin/openssl req -x509 -nodes -days 1825 -newkey rsa:2048 -keyout /etc/nginx/ssl/proxy.key -out /etc/nginx/ssl/proxy.pem -config /etc/nginx/ssl/proxy.conf
# Start and enable nginx
sudo /usr/bin/systemctl start nginx
sudo /usr/bin/systemctl enable nginx
