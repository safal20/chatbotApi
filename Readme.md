# Deployment guide for Chatbot
---

## This guide is for Ubuntu 16.04 LTS

### Installing pip

We need to update the package list before installing pip. This can be done by
```sh
sudo apt-get update
```

Now we can install pip for Python3 and update it to the latest version
```sh
sudo apt-get install python3-pip
sudo pip3 install --upgrade pip
```

### Installing Virtualenv and Virtualenvwrapper
Virtualenv and Virtualenvwrapper give us a framework for creating and using virtual environments so our system does not get affected. These can be installed by
```sh
sudo pip3 install virtualenv virtualenvwrapper
```

We need to export the paths for Virtualenvwrapper into the shell initialization script. This can be done by:
```sh
echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> ~/.bashrc
echo "export WORKON_HOME=~/Env" >> ~/.bashrc
echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
```

Now we reload the current shell using:
```sh
source ~/.bashrc
```

### Cloning the code repository from Git

We need to clone the git project into out system before we can deploy it. We need to install git first.
```sh
sudo apt-get install git
```

Now we can clone the git repository.
```sh
git clone https://github.com/safal20/chatbotApi.git
```
Place the secrets.json file and media folder into the directory ~/chatbotApi/chatBotAPi using filezilla.

### Creating and Setting Up a Virtual Environment
We can create a new virtual environment using mkvirtualenv command.
```sh
mkvirtualenv chatbotvenv
```
To activate the virtual environment we use the workon command, and to deactivate it we use deactivate.
```sh
workon chatbotvenv
deactivate chatbotvenv
```

Now we need to activate the virtual environment and install the requirements.
```sh
workon chatbotvenv
cd chatbotApi/
pip3 install -r requirements.txt
```

We can test the project by runnign a test server. Use Ctrl+C to exit.
```sh
python manage.py runserver
```

Now deactivate the virtual environment.

```sh
deactivate
```

### Installing and setting up uWSGI

uWSGI is the application container and supervisor for the project. We need to install it and configure it to use our django application.
```sh
sudo pip3 install uwsgi
```

We can test the installation by using the following command. We assume that the username is ubuntu, and the git project was cloned in the /home/ubuntu directory. Press Ctrl+C to exit.
```sh
uwsgi --http :8080 --home /home/ubuntu/Env/chatbotvenv --chdir /home/ubuntu/chatbotApi/chatBotAPi -w config.wsgi
```

Now we need to create config files for uWSGI in the directory /etc/uwsgi/sites
```sh
sudo mkdir -p /etc/uwsgi/sites
cd /etc/uwsgi/sites
```

In this directory, we place our configuration files. Create a file using any text editor.
```sh
sudo nano api.ini
```

The contents of this files are:
```txt
[uwsgi]
project = chatbotApi/chatBotAPi
base = /home/ubuntu

chdir = %(base)/%(project)
home = %(base)/Env/chatbotvenv
module = config.wsgi:application

master = true
processes = 5

socket = %(base)/%(project)/chatbot.sock
chmod-socket = 666
vacuum = true
```

We need to create a startup and control script for uWSGI too. For this we need to place uwsgi.service file in the directory /etc/systemd/system
```sh
sudo nano /etc/systemd/system/uwsgi.service
```

The contents of this file are:
```txt
[Unit]
Description=uWSGI Emperor service
After=syslog.target

[Service]
ExecStart=/usr/local/bin/uwsgi --emperor /etc/uwsgi/sites
Restart=always
KillSignal=SIGQUIT
Type=notify
StandardError=syslog
NotifyAccess=all

[Install]
WantedBy=multi-user.target
```
### Installing and Configuring Nginx
Now that we have configured uWSGI, we cam now install Nginx and set it up as a reverse proxy.
```sh
sudo apt-get install nginx
```

Let's create the Nginx configuration files for our project.
```sh
sudo nano /etc/nginx/sites-available/api
```

Assuming that the server URL is 13.126.63.68, the contents of this file are as follows. Replace the address with the server URL
```txt
server {
    listen 80;
    server_name 13.126.63.68;

    location = /favicon.ico { access_log off; log_not_found off; }

    location / {
        include         uwsgi_params;
        uwsgi_pass      unix:/home/ubuntu/chatbotApi/chatBotAPi/chatbot.sock;
    }
}
```

Next, we link the file in sites-available to sites-enabled directory.
```sh
sudo ln -s /etc/nginx/sites-available/api /etc/nginx/sites-enabled
```

### Starting Up and Controlling Services

Now that we have set up everything, we need to start the services. To start uWSGI, we use systemctl.
```sh
sudo systemctl start uwsgi.service
```

To refresh Nginx, we have to restart it.
```sh
sudo service nginx restart
```
The server is now ready. We can test this by sending a POST request to the server url at the path /api/chat/

***

Nginx and uWSGI services can be restarted using the commands
```sh
sudo systemctl restart uwsgi.service
sudo service nginx restart
```

The services can be stopped using the commands
```sh
sudo systemctl stop uwsgi.service
sudo service nginx stop
```
