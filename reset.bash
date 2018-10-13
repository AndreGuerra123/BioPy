#!/bin/bash

#delete previous migrations
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete

#reset database 
psql postgres://$DB_USER:$DB_PASS@$DB_HOST:$DB_PORT/$DB_NAME -c "drop owned by $DB_USER"

#make initial migrations 
python manage.py makemigrations
python manage.py migrate

#make custom data migrations
cp -a ./BioPyApp/migrations_templates/. ./BioPyApp/migrations/
python manage.py migrate

#run server
python manage.py runserver