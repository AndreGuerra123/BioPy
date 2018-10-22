source ./.env

#delete previous migrations
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete

#reset database 
psql postgresql://$USER:$PASS@$DB_HOST:$DB_PORT/$DB_NAME -c "drop owned by $USER"

#make initial migrations 
python manage.py makemigrations
python manage.py migrate

#make custom data migrations
cp -a ./BioPyApp/migrations_templates/. ./BioPyApp/migrations/
python manage.py migrate

#collect static
python manage.py collectstatic

#run server
python manage.py runserver