# AlleCena
---

### What am I looking at?
Hello Stranger,

this is AlleCena, abreviated from polish 'Ale cena'(what a price!).
It's a tool for statistical analysis and tracking of the most popular polish online auction system allegro.pl

Awarded in 2015 during [BrainCode Mobi 2015] (https://allegro.tech/braincode/2015/#toc_11) as the best application in category 'Allegro'

Application features:
* **price evaluation** at which user should sell a desired item
* **sell probability** estimation
* **price trends** chart
* **auction characteristics** - points out most important auction characteristics boosting sell success
* **auction tracking** ie. periodical checks of auction state and user notification
* basic statistical data

And all the above, given just user account and scarce information like item name and whether was it used or does it have a warranty


### Authors
Main authors:
* Grzegorz Wójcicki
* Krzysztof Bijakowski

Initally helped out with the project:
* Grzegorz Gurgul
* Natalia Stawowy
* Kamil Kopczyk


### Tech

* Virtually any relational database (config change required)
* Django & Django Rest Framework
* Celery & RabbitMQ
* Memcache | Redis

### Environment preparation

#### Gentoo
```sh
echo "dev-python/python sqlite" >> /etc/portage/package.use/python
emerge -avuDN @system
emerge -av dev-python/pip dev-python/virtualenv virtual/lapack virtual/cblas net-misc/rabbitmq-server net-misc/memcached dev-libs/libmemcached
rabbitmq-plugins enable rabbitmq_management

git clone https://rikkt0r@bitbucket.org/rikkt0r/allecena.git
cd allecena
virtualenv -p /usr/bin/python2.7 env
. env/bin/activate
pip install -r requirements.txt
```

#### Debian/[...]buntu

```sh
aptitude install python-distlib python-setuptools python-dev liblapack3 liblapacke liblapacke-dev libatlas-base-dev gfortran libblas-common libblas3 g++ libyaml-dev rabbitmq-server memcached libmemcached-dev libjpeg-dev zlib1g-dev
rabbitmq-plugins enable rabbitmq_management
easy_install pip virtualenv
git clone https://rikkt0r@bitbucket.org/rikkt0r/allecena.git
cd allecena
virtualenv -p /usr/bin/python2.7 env
. env/bin/activate
pip install -r requirements.txt
```

#### OSX

```sh
sudo brew install rabbitmq memcached
rabbitmq-plugins enable rabbitmq_management
pip install virtualenv
git clone https://rikkt0r@bitbucket.org/rikkt0r/allecena.git
cd allecena
virtualenv -p /usr/bin/python2.7 env
. env/bin/activate
pip install -r requirements.txt
```

### Queue overview
http://localhost:15672

### User and permissions at rabbitMq
```
rabbitmqctl add_user allecena allecenaPassword
rabbitmqctl add_vhost allecena
rabbitmqctl set_permissions -p allecena allecena ".*" ".*" ".*"

rabbitmqctl delete_user guest
rabbitmqctl add_user rikkt0r rikkt0rPassword
rabbitmqctl set_permissions -p allecena rikkt0r ".*" ".*" ".*"
rabbitmqctl set_permissions -p / rikkt0r ".*" ".*" ".*"
rabbitmqctl set_user_tags rikkt0r administrator
```

### Mysql config
```
[mysqld]
transaction-isolation = READ-COMMITTED
```

### Before running
Set the following variables in app/deploy_settings (well.. add it to gitignore?)
* ALLEGRO_PASSWORD_HASH
* ALLEGRO_KEY
* ALLEGRO_LOGIN


#### Running in debug

```sh
. env/bin/activate
# if run for first time
# creates database
python app/manage.py migrate
# loads test user (test@allecena.com / qwerty) and auction categories
python app/manage.py loaddata categories.yaml users.yaml
# endif

# three separate instances
python app/manage.py celeryd --verbosity=2 --loglevel=DEBUG -c 8
python app/manage.py celerybeat --verbosity=2 --loglevel=DEBUG
python app/manage.py runserver

# btw. api docs are available on /docs
```

### Deploy
What you do with our code is up to you. Anyway, if you plan to deploy it we recommend the following:
(example configs are available in top level directory ```deploy/```)
* Host base application using Apache + mod_wsgi
* Use any relational database django supports ex. postgres, mysql
* Install RabbitMQ and apply required permissions
* Spawn Celeryd workers using supervisor
* Keep CeleryBeat alive also using supervisor
* Install Memcache or Redis as celery result backend


#### Additional commands
```sh
python app/manage.py clear_cache
python app/manage.py allegro_print_countries
python app/manage.py allegro_update_categories
```

## TODO

* Migrate to Docker
* Tests :-)
* Create grabber and container for Ebay (fill ac_engine_ebay)
* Denormalize TriggerValues table
* Create a backend for country choosing (new db table & mainly config propagation to grabbers)
* Translations
