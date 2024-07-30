## Setting Up the Ubuntu Server

Create directory /var/www/ddoaudit.com/server
Create directory /var/www/ddoaudit.com/client

Update Droplet:
sudo apt-get update
sudo apt-get upgrade
sudo apt-get dist-upgrade

Install Docker: https://docs.docker.com/engine/install/ubuntu/
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

## Install and Run Certbot
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
sudo certbot certonly --standalone
sudo certbot renew --dry-run

## Running Docker Project
cd /var/www/ddoaudit.com/html/
docker compose up --build