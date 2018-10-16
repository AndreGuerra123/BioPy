import os
from django.db import migrations

def update_site(apps, schema_editor):
    SiteModel = apps.get_model('sites', 'Site')
    SiteModel.objects.update_or_create(id=os.getenv('SITE_ID'),
    defaults={'domain':os.getenv('SITE_DOMAIN'),'name':os.getenv('SITE_NAME')})


class Migration(migrations.Migration):

    initial =True

    dependencies = [
        ('BioPyApp', '0001_initial'),
        ('sites', '0002_alter_domain_unique')
    ]

    operations = [
        migrations.RunPython(update_site),
    ]