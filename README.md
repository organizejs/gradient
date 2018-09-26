# Development (Setting up your environment)
This page goes over how you would setup your dev environment on a Linux Centos machine.

## Postgres
1. Install and Setup postgres

    a. Install postgres
    ```sh
    # CentOS
    sudo yum update
    sudo yum install postgresql postgresql-server postgresql-devel postgresql-contrib postgresql-docs
    
    # Ubuntu
    sudo apt-get update
    sudo apt-get install postgresql postgresql-contrib
    ```
    b. Once the above installation completes, initialize the DB
    ```sh
    sudo service postgresql initdb
    ```
    d. (CentOS only) Edit pg_hba.conf
    ```sh
    sudo vim /var/lib/pgsql9/data/pg_hba.conf
    ```
    Edit the file to look like this:
    ```conf
    # TYPE  DATABASE        USER            ADDRESS                 METHOD
 
    # "local" is for Unix domain socket connections only
    local   all             all                                     trust
    # IPv4 local connections:
    host    all             all             127.0.0.1/32            trust
    # IPv6 local connections:
    host    all             all             ::1/128                 trust
    ```
    e. Edit postgresql.conf
    ```sh
    # Ubuntu
    sudo vim /etc/postgresql/9.x/main/postgresql.conf
    
    # CentOS
    sudo vim /var/lib/pgsql9/data/postgresql.conf
    ```
    Uncomment and edit so that it looks as follows:
    ```conf
    listen_addresses='*'
    port=5432
    ```
    f. (Optional if you plan to use pgAdmin) Allow 0.0.0.0/0 so that pgAdmin can access the local server. Edit the following:
    ```conf
    # for Ubuntu
    sudo vim /etc/postgresql/9.x/main/pg_hba.conf
    
    # for CentOS
    sudo vim /var/lib/pgsql9/data/pg_hba.conf
    ```
    Add the following line in `pg_hba.conf`
    ```conf
    host all all 0.0.0.0/0 md5
    ```
    You will also have to make sure that port 5432 on your local machine/VM is accessible.

2. Start (or restart) PostgreSQL Server
```sh
sudo service postgresql start
sudo service postgresql restart
```

3. Login into Postgres user (This will also be the command to open psql to interact with your postgres db):
```sh
sudo su - postgres
psql -U postgres
```

4. Change password on postgres user:
```
ALTER USER postgres WITH PASSWORD 'password';
```

5. Create your database for Gradient:
```sh
./run db:create #or use db:reset if that doesnt work
```

## Flask application
1. Install SASS and Dependencies

Ubuntu:
```sh
sudo apt-get install ruby-full build-essential rubygems
sudo gem install sass
````
CentOS:
```sh
# Install deps
yum install libyaml libyaml-devel openssl libxml2-devel bison libxslt-devel openssl-devel tcl tk libffi tcl-devel tk-devel libffi-devel

# Download Ruby
cd /usr/local/src/
wget http://ftp.ruby-lang.org/pub/ruby/1.9/ruby-1.9.3-p392.tar.gz
tar -xvzf ruby-1.9.3-p392.tar.gz
cd ruby-1.9.3-p392

# Compile Ruby from Source
./configure
make
make test
make install
ruby -v

# Install things for SASS
gem install bundler
gem install sass
gem install listen
```

2. Install requirements
```sh
# if pip is pip3
pip install -r requirements.txt

# otherwise
python3 -m pip install -r requirements.txt
``` 
3. Setup and populate a secrets/config.py file:
```sh
mkdir secrets
touch secrets/config.py
```
The file should have the following:
```python
from .base import BaseConfig

class Config(BaseConfig):
    DEBUG = [True/False]
    DEBUG_ASSETS = True
    SECRET_KEY = [ex 'secret']
    MAIL_SERVER = [ex 'smtp.mandrillapp.com' - based on mailchimp account]
    MAIL_USERNAME = [ex 'Gradient' - based on mailchimp account]
    MAIL_PASSWORD = [ex 'some_guid' - based on mailchimp account]
    MAIL_DEFAULT_SENDER = [ex 'info@gradient.care' - based on mailchimp account]
    SQLALCHEMY_DATABASE_URI = "postgresql://gradient_user:password@localhost:5432/gradient_dev"
    SECURITY_PASSWORD_SALT = [ex 'secret']
    SECURITY_EMAIL_SENDER = [ex 'info@gradient.care' - based on mailchimp account]
    STRIPE_PUBLIC_KEY = [ex 'pk_test_some_guid' - based on stripe account]
    STRIPE_SECRET_KEY = [ex 'sk_test_some_guid' - based on stripe account]
    MAILCHIMP_KEY = [ex 'some_guid' - based on mailchimp]
    MAILCHIMP_USERNAME = [ex 'user@gradient.care' - based on mailchimp]
    MAILCHIMP_UNREGISTERED_LIST_ID = [ex 'some_guid' - based on mailchimp]
    MAILCHIMP_REGISTERED_LIST_ID = [ex 'some_guid' - based on mailchimp]
    TX_SECRET_KEY = [ex 'some_guid']
```
4. Run locally
```sh
python application.py
```

## Additional References
- [Setting up postgreSQL on AWS instance](https://www.quora.com/How-can-I-install-PostgreSQL-on-AWS-EC2-and-how-can-I-access-that)

---

# Deployment 
This page goes over how you would deploy to AWS EBS. (As of 01/01/18) Gradient is deployed on AWS EBS on three environments: Production, Staging, and Devenv. 

## Deployment (to EBS)
1. Install the EB CLI

2. Download your AWS security credentials from the AWS console (this will require having an IAM user designated by the account owner) - [more information here](https://docs.aws.amazon.com/general/latest/gr/aws-security-credentials.html)

3. In ~/.aws create a file titled: 'config'
```sh
touch ~/.aws/config
```
Add the following in the file:
```yml
[profile eb-cli]
aws_access_key_id = your_aws_access_key_id
aws_secret_access_key = your_aws_secret_access_key
```
4. In your project directory, create the file .elasticbeanstalk/config.yml
```sh
touch .elasticbeanstalk/config.yml
```
Add the following in the file:
```yml
branch-defaults:
  dev:
    environment: devenv
  master:
    environment: production
    group_suffix: null
  staging:
    environment: staging
global:
  application_name: gradient
  branch: null
  default_ec2_keyname: null
  default_platform: python3.4
  default_region: us-east-1
  include_git_submodules: true
  instance_profile: null
  platform_name: null
  platform_version: null
  profile: eb-cli
  repository: null
  sc: git
  workspace_type: Application
```

## Using EB-CLI
- To view logs, run `eb logs -a`
- Create an environment with `eb create <ENV NAME>`, e.g. `eb create staging`


To deploy:

- Switch to the branch you want to deploy
- Pull the latest changes / make sure that the changes you wish to deploy are committed
- Run `eb deploy <ENV NAME>`

Alternatively, configure certain branches to deploy to certain environments:

```
git checkout <BRANCH>
eb use <ENV NAME>
```

Then you can just do `eb deploy` from a branch.

The deployed app looks for Flask config variables in the environment. You can set these in the Elastic Beanstalk dashboard for an environment (`Configuration > Software Configuration` and scroll to the bottom). The config variables should be prefixed with `FLASK_`, e.g. to set the `SECRET_KEY` config variable, set an env var called `FLASK_SECRET_KEY`.

---

## Additional References
- [Setting up the `eb cli`](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-configuration.html)
