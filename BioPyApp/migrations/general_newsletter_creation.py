import os
from django.db import migrations

def general_newsletter_creation(apps,schema_editor):
    Newsletter = apps.get_model('newsletter', 'Newsletter')
    Site = apps.get_model("sites","Site")
    site=Site.objects.get(id=os.environ['SITE_ID'])
    general_newsletter = Newsletter.objects.create(title="General",slug="general",email=os.environ['DB_EMAIL'],sender=os.environ['DB_NAME'])
    general_newsletter.site.set([site])

class Migration(migrations.Migration):

    dependencies = [
        ('BioPyApp', 'sites_update'),
        ('BioPyApp', 'superuser_creation'),
        ('newsletter','0001_initial')
    ]

    operations = [
        migrations.RunPython(general_newsletter_creation)
    ]
