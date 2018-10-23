from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms.models import InlineForeignKeyField
from urllib.parse import urlparse
from django.core.exceptions import ValidationError

class Endpoint(models.Model):
    POLICIES=[('POLICY1','policy'),('POLICY2','policy2')]
    MODES=[('MODE1','Mode1')]
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    url = models.CharField(max_length=200)
    policy = models.CharField(choices=POLICIES,max_length=50)
    mode = models.CharField(choices=MODES,max_length=50)
    certificate = models.FileField(blank=True,null=True)
    private_key = models.FileField(blank=True,null=True)
    server_certificate = models.FileField(blank=True,null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def validate_unique(self,exclude=None):
        existing = [ep.url for ep in Endpoint.objects.filter(owner=self.owner)]
        if not self.unique_url(self.url,existing):
            raise ValidationError({'url':['Endpoint url must have unique hostname, port and path combination per user.',]})
    
    def unique_url(self,url,urls):
        for urlt in urls:
            if self.is_equal_url(url,urlt):
                return False
        return True

    def is_equal_url(self,url1,url2):
        url1_parsed = urlparse(url1)
        url2_parsed = urlparse(url2)
        if(url1_parsed.netloc == url2_parsed.netloc and url1_parsed.path==url2_parsed.path):
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        self.validate_unique()
        super(Endpoint, self).save(*args, **kwargs)

        

class Node(models.Model):
    TYPES=[("variable","Variable"),("classsifier","Classifier"),("event","Event"),("spectrum","Spectrum")]
    endpoint = models.ForeignKey(to=Endpoint,on_delete=models.CASCADE)
    nodeid = models.CharField(max_length=100)
    type = models.CharField(choices=TYPES, max_length=10)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together= ('endpoint','nodeid')

class Process(models.Model):
    PROCESS_TYPES=(
        ('R','Raw Materials'),
        ('C','Cleaning'),
        ('U','Upstream'),
        ('D','Downstream'),
        ('P','Packaging'),
    )
    owner = models.ForeignKey(
       User,
        on_delete=models.CASCADE,
    )
    name = models.CharField(unique=True,max_length=25)
    scale = models.PositiveIntegerField()
    type = models.CharField(choices=PROCESS_TYPES,max_length=1)
    upstream = models.ForeignKey('Process',blank=True, null=True, on_delete=models.DO_NOTHING, related_name='+')
    downstream = models.ForeignKey('Process',blank=True, null=True,  on_delete=models.DO_NOTHING,related_name='+')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Processes"

    def __str__(self):
        return " : ".join([str(self.id), self.name, self.owner.username, self.modified.replace(microsecond=0).isoformat(' ')])

class Batch(models.Model):
    process = models.ForeignKey('Process',on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    start = models.DateTimeField()
    end = models.DateTimeField(blank=True,null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together=('process','name')
        verbose_name_plural = "Batches"

    def __str__(self):
        return " : ".join([str(self.id), self.name, self.process.name, self.modified.replace(microsecond=0).isoformat(' ')])

class Variable(models.Model):
    batch = models.ForeignKey('Batch',on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    timestamp = models.DateTimeField()
    value = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together=('batch','name','timestamp')

    def __str__(self):
        return " : ".join([str(self.id), self.batch.process.name, self.batch.name, self.name, str(self.value), self.timestamp.replace(microsecond=0).isoformat(), self.modified.replace(microsecond=0).isoformat(' ')])

class Event(models.Model):
    batch = models.ForeignKey('Batch',on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    timestamp = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together=('batch','name','timestamp')

    def __str__(self):
        return " : ".join([str(self.id), self.batch.process.name, self.batch.name, self.name, self.timestamp.replace(microsecond=0).isoformat(), self.modified.replace(microsecond=0).isoformat(' ')])
   
class Class(models.Model):
    batch = models.ForeignKey('Batch',on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    value = models.CharField(max_length=25)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together=('batch','name')
        verbose_name_plural = "Classes"

       
    def __str__(self):
        return " : ".join([str(self.id), self.batch.process.name, self.batch.name, self.name, srt(self.value),self.timestamp.replace(microsecond=0).isoformat(), self.modified.replace(microsecond=0).isoformat(' ')])

