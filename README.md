sudo apt update && sudo apt upgrade -y
sudo apt install python3
sudo apt install python3-pip
sudo pip3 install virtualenv
sudo apt install postgresql postgresql-contrib -y
su - postgres
psql -U postgres
\password postgres
\q
exit
cd /etc/postgresql/12/main
sudo ci postgresql.conf

<!-- connection and authentication
listen_addresses = '*'
:wq -->

sudo vi pg_hba.conf

<!--
Type    DB      USER    ADDRESSE    METHOD
local   all     postgres            md5
local   all     all                 md5
local   all     all     0.0.0.0/0   md5     IPv4
local   all     all     ::/0        md5     IPv6
:wq -->

systemctl restart postgresql

adduser masabi
usermod -aG sudo masabi
su - masabi

mkdir app
cd app/
virtualenv venv
ls -la
source venv/bin/activate
deactivate
mkdir src
cd src/

git clone url .

cd ..
source venv/bin/activate
cd src/
pip install -r requirements.txt
uvicorn --host 0.0.0.0 app.main:app

set environment variables
vi .profile
set -o allexport; source /path/to/.env; set +o allexport
:wq

cd src/
alembic upgrade head

pip install httptools uvloop gunicorn -y

gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000

create a service
cd /etc/systemd/system/
sudo vi api.service
systemctl start api
systemctl enable api

pip install nginx -y
cd /etc/nginx/sites-avaiblable/
cat default
