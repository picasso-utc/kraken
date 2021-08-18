# Kraken API

## Installation

### Prerequisites

First of all, you need to set up the environment.
You will need [Python version 3](https://www.python.org/downloads/) and [pip (a Python packages manager)](https://pypi.org/project/pip/).


Then we will set up the virtual environment with `virtualenv`.
```sh
pip install virtualenv
```

Create the `venv` folder :
On Linux :
```sh
virtualenv -p python3 "venv"        # python3 is the name of python executable
```
On Windows :
```sh
virtualenv "venv"
```

Now activate the virtual environment. You have to do this everytime you want to work with Woolly and don't see the `(venv)` on the left of your terminal prompt.
```sh
# On Linux :
source venv/bin/activate
# On Windows :
venv\Scripts\activate
```


### Installation

With the virtual environment activated, install all the required librairies :
```sh
pip install -r requirements.txt
```


Now ask a responsible person for the `settings_confidential.py` file containing the foreign APIs identification keys. The file is to be placed next to the `settings.py` file. There is a placeholder file called `settings_confidential.example.py`, you can copy and fill it. 

Connect to postgres and create the `kraken` database

```shell
psql postgres
```

```sql
CREATE DATABASE kraken ENCODING='UTF8';
```

### You now have 2 choices

#### Start with empty tables
```sh
python manage.py migrate
```

#### Take datas from the distant server
```shell
# connect to the production server and run
pg_dump kraken -U postgres -h localhost -F c > backup.sql
# on your machine
scp root@37.139.25.111:/root/backup.sql ./
pg_restore -U victor -d kraken -1 ~/backup.sql
```
If you have problems with some migrations 'contains null values', update the database (in local) that got the issue
```
UPDATE x SET y='-' where y Is Null;
```
If you check your local database kraken you should see real data from the production.

You also need to generate all static files :
```sh
python manage.py collectstatic
```

Finally, you can launch the server.
```sh
python manage.py runserver
```

You can now play with the server on http://localhost:8000


## Deployment
There are two files you have to check on the server if there is a problem with kraken: 
- rc.local in /etc/ : this one allows the server to run the script which launch the screen for kraken.
- start-kraken.sh in etc/init.d/ : this one contains the command which are run at the launch of the server. It consists in a screen which run kraken permanently after restarting apache2 (because it starts nginx by default). You shoulkd check also if the port 8080 is already occupied by an other app, in order to avoid concurrency with apache2.

## How to create a feature
### (Optional) Create a new module
As you can see kraken is divided in different modules (tv, treso, perm..) gather in one app (core).
If you are about to create a complex new feature in kraken you should create a dedicated module with
```shell
python3 manage.py startapp <name of your module>
```
Add your new app to INSTALLED_APPS in core/settings.py
```python
INSTALLED_APPS = [
    ...,
    '<name of your module>'
]
```

### Create / edit a model
In each module you will find a models file that contains 'the structure of your database'

You can create or edit a class [see](https://docs.djangoproject.com/en/3.2/topics/db/models/) for more informations

After that you can generate all migrations files with
```shell
python manage.py makemigrations <name of your module>
```
Then run the migrations with
```shell
python manage.py migrate
```
You should now have your table in your db under the name <name of your module>_<name of your model>

### Create your route


## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details
