import os
from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_db_superuser(apps, schema_editor):
     User = apps.get_registered_model('auth', 'User')
     EmailAddress = apps.get_registered_model('account','EmailAddress')

     user = User(
         username=os.getenv('USER'),
         email=os.getenv('EMAIL'),
         password=make_password(os.getenv('PASS')),
         is_superuser=True,
         is_staff=True,
         is_active=True
     )
     user.save()
     EmailAddress.objects.create(user=user,email=user.email,primary=True,verified=True)

class Migration(migrations.Migration):

     dependencies = [
         ('BioPyApp','sites_update'),
         ('auth', '0001_initial'),
         ('account','0001_initial')
     ]

     operations = [
         migrations.RunPython(create_db_superuser),
     ]