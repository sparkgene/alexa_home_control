#! /bin/bash

sudo apt-get install -y nodejs npm
wget https://www.symantec.com/content/en/us/enterprise/verisign/roots/VeriSign-Class%203-Public-Primary-Certification-Authority-G5.pem -O certs/ca.pem
cp service/alexa_home.service /etc/systemd/system/alexa_home

systemctl enable alexa_home

systemctl start alexa_home
