# Overview
User can transfer balance now or later in bulk. After every successful transfer a transaction history will be created for both the accounts. Cash transaction(withdrawal or deposit) option is also available. In case of transfer failure no transaction history will be created and source account's balance will be adjusted.


# Features:
- Account Creation
- Instant Balance Transfer
- Scheduled Balance Transfer
- Multiple transfers in a single request
- Cash Transaction (deposit or withdrawal)
- Multiple cash transaction in a single request
- Transaction History of every transaction takes place in database
- **Unit Test included**

# How to run

#### preparing django server
```sh
git clone git@github.com:omariut/Schedule-Balance-Transfer-API.git
cd Schedule-Balance-Transfer-API
virtualenv venv
pip install requirements.txt
python manage.py makemigration
python manage.py migrate
python manage.py runserver
```

#### prepearing celery
run the below commands in two different terminals
```sh
celery -A picha worker -l info
```
```sh
celery -A picha beat -l info
```
#### install redis server
https://redis.io/download/


#### run redis server
```sh
redis-server
```
# Documentation:
- link : http://localhost:8000/swagger
- Enter data from data_entry.json

