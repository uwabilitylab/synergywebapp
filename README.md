# Synergy Web App
The Synergy Web App can be run on any machine that supports Python and the Flask framework.  This setup is written for
Amazon EC2 instances running Amazon Linux 2 with the `yum` package manager, but may be easily adapted for any major
Linux distribution.

You can view a demo of this app in action at [https://synergy.me.uw.edu](https://synergy.me.uw.edu).

## Setting Up: What You'll Need
 * An account with Amazon Web Services or other cloud provider
 * A basic understanding of setting up compute instances on your cloud provider
 * A basic understanding of Linux package managers such as Yum or Apt
 * root access on your server

NOTE: unless otherwise specified, all commands are intended to be run as root.

## Server Instance Setup
*These instructions are specifically for Amazon Web Services – if you are using another cloud provider you'll need to follow their process for creating computing instances.*
Go to your AWS Console and navigate to EC2. Click the **Launch Instance** button to get started.
1. **Choose an Amazon Machine Image**: select the **Amazon Linux AMI** option.
2. **Choose an Instance Type**: t1.micro is the minimum required size, however for optimal performance we recommend using t2.medium or higher.  Click **Next** to continue.
3. **Configure Instance Details** (optional): configure your desired details here.  Then click **Next**.
4. **Add Storage**: Your instance will be provided with an 8GiB unencrypted volume by default.  You'll need a larger—preferably encrypted—volume to hold the app and any uploaded data files.  Click **Add New Volume** to add a new EBS volume: select `General Purpose SSD` as the Type, and set `Size` to 20GiB or more.  Using `Encryption` is strongly recommended.  *Optional: for instances with 1GiB or less of memory, we recommend creating an additional 1GiB volume for Swap data.*  Click **Next**.
5. **Add Tags** (optional): configure the desired tags for the instance here.  Then click **Next**.
6. **Configure Security Group**: Click `Add Rule`, then select under `Type` select `HTTP` and `Anywhere` for `Source`.  Repeat this step, selecting `HTTPS` as the `Type`.  This will ensure people can view your new website!.  Click **Review and Launch**.
7. **Review Instance Launch**: Double check everything looks good and hit **Launch** to launch your new server!


## Server Configuration
NOTE: all the below commands must be run as the `root` user.


### Install packages
First enable the yum EPEL repositories by following the instructions [here](https://aws.amazon.com/premiumsupport/knowledge-center/ec2-enable-epel/).
Then run `yum update` to update the server package list.

The app relies on Python 3.6 and several other packages to run.  Install them with Yum:
```
yum install -y nginx.x86_64 python36 python36-devel python36-pip gcc git pcre pcre-devel upstart
```

### Configure Volumes and File System
IMPORTANT: please check the names of the volumes before running any of these commands.  On our server our data volume was `/dev/sdb` and our swap volume was `/dev/sdf`.

1. Partition and format the data volume
	```
	fdisk /dev/sdb
	mkfs -t ext4 /dev/sdb1
    ```
    *optional*: if you added a swap volume, format it with `mkswap`
    ```
    fdisk /dev/sdf
    mkswap /dev/sdf1
    ```
2. Create a directory for the app and its data to reside on
    ```
    mkdir /mnt/data
    ```
3. Add the following lines to `/etc/fstab`
    ```$xslt
    /dev/sdb1    /mnt/data   ext4    defaults,noatime 1  2
    ```
    *optional*: if you added a swap volume when setting up the server, you'll need to add add an additional line to `/etc/fstab`:
    ```$xslt
    /dev/sdf1    none        swap    sw              0   0
    ```
4. Mount all the new volumes: `mount -a`
5. Create a directory for the webserver
    ```
    mkdir /mnt/data/www
    ```
6. Check out the app's code from GitHub
    ```
    git clone https://github.com/uwabilitylab/synergywebapp /mnt/data/www/synergywebapp
    ```


### Install additional Python packages
Python includes a package manager (Pip) which you can use to easily install the required Python packages.

Run this command to install all necessary Python dependencies:
```
pip3 install alembic click cycler dominate Flask Flask-Bootstrap Flask-Login Flask-Migrate Flask-Moment Flask-SQLAlchemy Flask-WTF itsdangerous Jinja2 kiwisolver Mako MarkupSafe matplotlib numpy pandas pip pyparsing python-dateutil python-editor pytz scikit-learn scipy setuptools six sklearn SQLAlchemy uWSGI visitor Werkzeug WTForms xlrd
```


### Generate SSL Certificates
For maximum security, we strongly recommend running the app over HTTPS.  These instructions show how to obtain a (free) SSL certificate from [LetsEncrypt](https://letsencrypt.org/).

1. Download the LetsEncrypt utility
    ```
    git clone https://github.com/letsencrypt/letsencrypt
    ```
2. Run the LetsEncrypt utility by typing
    ```
    sudo letsencrypt/letsencrypt-auto --debug
    ```
    and follow the prompts to create your SSL certificates.  *IMPORTANT*: make note of the paths to the key and certificate – you'll need these later!


### Configure the App
The app runs as a CGI script using uWSGI, with Nginx used as a proxy and for SSL termination.

#### Flask Setup
The app uses the [Flask](http://flask.pocoo.org/) Python framework for running the app's main codebase.

##### Database Setup
Initialize the database with the following commands:
```
flask db init
flask db migrate -m"initial migration"
flask db upgrade
```

#### uWSGI
The app uses [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) to run the Flask framework in production deployments.

To set up the uWSGI service copy the `synergyapp.conf` file from the deploy/ directory into `/etc/init`:
```
cp /mnt/data/www/synergywebapp/deploy/synergyapp.conf /etc/init
```

#### Nginx
The app uses [Nginx](https://nginx.org/) as the external webserver and for SSL termination. Nginx communicates with uWSGI via a Unix socket file (`synergyApp.sock`), located in the app's `run/` directory.

##### SSL Configuration
*Optional:* Generate a dhparams file for improved HTTPS security in nginx:
```
cd /etc/ssl/certs
openssl dhparam -out dhparam.pem 4096
```

Using the paths from the previous **Generate SSL Certificates** step, update the nginx config file (`/mnt/data/www/synergywebapp/deploy/synergyapp_nginx.conf`) to use the correct paths to your SSL certificates.
```
ssl_certificate     /etc/letsencrypt/live/[my domain name]/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/[my domain name]/privkey.pem;
```
NOTE: if the above dhparams step is skipped, make sure to remove the line
```
ssl_dhparam conf.d/dhparams.pem;
```
from the `synergyapp_nginx.conf` file.

##### Copy the default Synergy Web App config file into place
IMPORTANT: Change the `server_name` to the domain name you will be using, and update the paths of `ssl_certificate` and `ssl_certificate_key` to point to your SSL certificates.

Then copy your updated configuration file to the nginx configuration folder:
```
cp /mnt/data/www/synergywebapp/deploy/synergyapp_nginx.conf /etc/nginx/conf.d/synergywebapp.conf
```

#### Final Preparation
Before running, we need to make a couple of final changes so Nginx can run the app properly.

Set up file permissions as needed:
```
# Make sure Nginx can write to the app's run/ directory:
chown -R nginx:ec2-user /mnt/data/www/synergywebapp/run
chmod 775 /mnt/data/www/synergywebapp/run

# Make sure Nginx can write to the file upload directory
chown nginx:ec2-user /mnt/data/www/synergywebapp/app/csvfiles
chmod 775 /mnt/data/www/synergywebapp/app/csvfiles
```

Start Nginx, and make sure it automatically starts up on a server reboot:
```
service nginx start
chkconfig nginx on
```

Set up a `systemd` service so the Synergy Web App starts up automatically on boot:
```
cp /mnt/data/www/synergywebapp/deploy/synergyapp.service /usr/lib/systemd/system/
systemctl enable /usr/lib/systemd/system/synergyapp.service
```

### Setting Up Admin Privileges
Each user must create an account in order to upload and process files. Every account must be approved by an administrator in order to do so. Before the website is public, first complete and run the script below to create and approve the `Admin` user.
```
from sqlalchemy import create_engine
from sqlalchemy.sql import update
import datetime

from app.models import User
from app import db

admin = User(username='Admin', email='YOUR_EMAIL_HERE', institution='YOUR_INSTITUTION_HERE', confirmed=True, confirmed_on=datetime.datetime.now(tz=None))
admin.set_password('YOUR_PASSWORD_HERE')

db.session.add(admin)
db.session.commit()
```
After confirming the `Admin` user, the website can be made public and all additional users can be confirmed by logging in as `Admin` and navigating to `/admin`

### Setting Up Email Privileges
Each time a new user is created an email is sent to the designated address to notify the administrator that a new account needs approval. Once the administrator approves the account an email is sent to the user notifying them that their account has been approved. In order to set this up the following variables must be exported in the console. Most emails will require `Less secure app access` to be turned on in order to login, and so it is suggested that this email not be used for other purposes.
```
export MAIL_SERVER=’YOUR_MAIL_SERVER’
export MAIL_PORT=587
export MAIL_USE_TLS=1
export MAIL_USERNAME='YOUR_EMAIL’
export MAIL_PASSWORD=‘YOUR_EMAIL_PASSWORD’
```

### Starting it All Up!

Export these variables
```
export BASE_FOLDER=‘YOUR_BASE_FOLDER'
export SECRET_KEY=‘YOUR_SECRET_KEY’
```

You can start the application by running the command
```
start synergyapp
```

In order to process uploaded files, you'll also need to run daemon.py in the background.  We do this using [GNU screen](https://www.gnu.org/software/screen/).
Install screen by running
```
yum install screen
```

Then start up a new instance of screen by typing:
```
screen -S synergyapp
```
Screen will launch and you'll be presented with another command prompt.  To run the daemon, navigate to the app directory and type
```
python3 daemon.py
```
To leave the daemon running in the background, detach the screen by typing `Ctrl-v` then the `d` key.  You can return
to the screen instance by typing
```
screen -r synergyapp
```

Then go to your browser and navigate to your domain name – if all went well you are all set up!


## Troubleshooting
The app logs all Python and other runtime errors to the `run/uwsgi.log` file.  If the app appears to start up correctly,
but some or all pages aren't running correctly, check this file for the possible cause.

You can also check the Nginx error log (`/var/log/nginx/error.log`) in case of startup or other errors.
