#! /bin/bash

# download ca certificate
wget https://www.symantec.com/content/en/us/enterprise/verisign/roots/VeriSign-Class%203-Public-Primary-Certification-Authority-G5.pem -O certs/ca.pem

# install packages
sudo apt-get install -y nodejs npm

npm install aws-iot-device-sdk

# setup daemon
cp -f service/alexa_home.service /etc/systemd/system/
systemctl enable alexa_home
systemctl start alexa_home
