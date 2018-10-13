import os
from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_db_superuser(apps, schema_editor):
     User = apps.get_registered_model('auth', 'User')
     admin = User(
         username=os.environ['DB_USER'],
         email=os.environ['DB_EMAIL'],
         password=make_password(os.environ['DB_PASS']),
         is_superuser=True,
         is_staff=True
     )
     admin.save()

class Migration(migrations.Migration):

     dependencies = [
         ('BioPyApp','sites_update'),
         ('auth', '0001_initial')
     ]

     operations = [
         migrations.RunPython(create_db_superuser),
     ]