import os
from django.db import migrations
from django.utils import timezone
from django.conf import settings
from django.core.files import File

def general_newsletter_creation(apps,schema_editor):
    Newsletters = apps.get_model('newsletter', 'Newsletter')
    Site = apps.get_model("sites","Site")
    site=Site.objects.get(id=os.getenv('SITE_ID'))
    general_newsletter = Newsletters.objects.create(email=os.getenv('EMAIL'),sender=os.getenv('SITE_NAME'),slug="general_newsletter",title="General Newsletter")
    general_newsletter.site.set([site])

def general_newsletter_initial_subscription(apps,schema_editor):
    Users = apps.get_model('auth','User')
    Newsletters = apps.get_model('newsletter', 'Newsletter')
    Subscriptions = apps.get_model('newsletter', 'Subscription')
    user = Users.objects.get(username=os.getenv('USER'))
    newsletter = Newsletters.objects.get(slug="general_newsletter")
    Subscriptions.objects.create(user=user,newsletter=newsletter,subscribed=True)
    
def general_newsletter_initial_message(apps,schema_editor):
    Messages = apps.get_model('newsletter','Message')
    Newsletters = apps.get_model('newsletter', 'Newsletter')
    newsletter = Newsletters.objects.get(slug="general_newsletter")
    Messages.objects.create(newsletter=newsletter,date_create=timezone.now(),date_modify=timezone.now(),slug="general_message",title="General Message")

def general_newsletter_initial_article(apps,schema_editor):
    Articles = apps.get_model('newsletter','Article')
    Messages = apps.get_model('newsletter', 'Message')
    message = Messages.objects.get(slug="general_message")
    Articles.objects.create(post=message,sortorder=1,text="If you are seeing this then newsletter in your e-mail all newsletter capabilities are working properly.",title="General Article")


def general_newsletter_initial_submission(apps,schema_editor):
    Submissions = apps.get_model('newsletter','Submission')
    Newsletters = apps.get_model('newsletter', 'Newsletter')
    Messages = apps.get_model('newsletter', 'Message')

    newsletter = Newsletters.objects.get(slug="general_newsletter")
    message = Messages.objects.get(title="General Message")

    Submissions.objects.create(message=message,newsletter=newsletter)

class Migration(migrations.Migration):

    dependencies = [
        ('BioPyApp', 'sites_update'),
        ('BioPyApp', 'superuser_creation'),
        ('newsletter','0001_initial')
    ]

    operations = [
        migrations.RunPython(general_newsletter_creation),
        migrations.RunPython(general_newsletter_initial_subscription),
        migrations.RunPython(general_newsletter_initial_message),
        migrations.RunPython(general_newsletter_initial_article),
        migrations.RunPython(general_newsletter_initial_submission)
    ]
