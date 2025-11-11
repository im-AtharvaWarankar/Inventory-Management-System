sudo apt update -y || exit 0;
sudo apt install wget curl -y || exit 0;
sudo apt install python3-pip python3-virtualenv python3-venv gunicorn -y || exit 0;
sudo apt-get remove docker docker-engine docker.io containerd runc -y
sudo apt-get install ca-certificates curl gnupg lsb-release -y || exit 0;
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg | exit 0;
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null || exit 0;
sudo apt-get update -y || exit 0;
sudo apt-get install docker-ce docker-ce-cli containerd.io -y || exit 0;
sudo usermod -aG docker $USER || exit 0;
sudo systemctl enable docker.service || exit 0;
sudo systemctl enable containerd.service || exit 0;
sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)"  -o /usr/local/bin/docker-compose
sudo mv /usr/local/bin/docker-compose /usr/bin/docker-compose
sudo chmod +x /usr/bin/docker-compose
sudo reboot now || exit 0;