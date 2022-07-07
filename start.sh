git clone git@github.com:omariut/Schedule-Balance-Transfer-API.git
cd Schedule-Balance-Transfer-API
virtualenv venv
pip install requirements.txt
python manage.py makemigration
python manage.py migrate
python manage.py runserver
