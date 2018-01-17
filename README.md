## Steps to deploy on EC2
Online reference

### Create EC2 instance
1. On EC2, Select "Amazon Linux AMI 2017.09.0 (HVM)" -> review and launch
2. Set security group (Online reference)
3. review -> set security pair or use existing pair
### 



```
ssh -i "ez-switch-ec2.pem" ec2-user@ec2-13-210-137-102.ap-southeast-2.compute.amazonaws.com

vim /etc/nginx/conf.d/virtual.conf

change to no sudo user and use aws instructions to install nvm, node
```

nocache pip install
install gcc

sudo apt-get install tesseract-ocr
sudo apt-get install libpng12-dev
sudo apt-get install libjpeg62-dev

EC2 Credential
account alias: ‎212252083097
user name: dev-ops
user password: EzSwitch2017

gunicorn app:app -b localhost:8000 -w 2 --threads 4
gunicorn app:app -b localhost:8000 -w 2 --threads 4 > console.log &


https://www.matthealy.com.au/blog/post/deploying-flask-to-amazon-web-services-ec2/