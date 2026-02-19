#!/bin/bash
set -e

sudo apt update
sudo apt install -y nginx docker.io

sudo systemctl enable nginx
sudo systemctl enable docker

echo "Custom AMI Built on $(date)" | sudo tee /var/www/html/index.html
