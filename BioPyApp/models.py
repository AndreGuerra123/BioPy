from urllib.parse import urlparse

import computed_property
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms.models import InlineForeignKeyField
from django_pandas.managers import DataFrameManager
from BioPyApp.common import minNum, maxNum, deltaEpoch
from BioPyApp.drivers.client import EndpointClient


TYPES=[("variable","Variable"),("class","Classifier"),("event","Event"),("spectrum","Spectrum")]


class Endpoint(models.Model):
    POLICIES=[('Basic128Rsa15','Basic128Rsa15'),
              ('Basic256','Basic256'),
              ('Basic256Sha256','Basic256Sha256')]
    MODES=[('Sign','Sign'),
           ('SignAndEncrypt','SignAndEncrypt')]

    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    url = models.CharField(max_length=200)
    policy = models.CharField(choices=POLICIES,max_length=50, blank=True, null=True)
    mode = models.CharField(choices=MODES,max_length=50, blank=True, null=True)
    certificate = models.FileField(blank=True,null=True)
    private_key = models.FileField(blank=True,null=True)
    server_certificate = models.FileField(blank=True,null=True)
    timeout = models.IntegerField(default=4)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def get_client(self):
        return EndpointClient(self)
        
    def get_unique_info(self,url):
        parsed = urlparse(url)
        return [parsed.hostname,parsed.port,parsed.path]

    def validate(self):
        existing_info = [self.get_unique_info(ep.url) for ep in Endpoint.objects.filter(owner=self.owner)]
        if self.get_unique_info(self.url) in existing_info:
            raise ValidationError({'url':['Endpoint url must have unique hostname, port and path combination per user.',]})
        
        all_together=['policy','mode','certificate','private_key']
        if any([getattr(self, field, None) for field in all_together]) and not all([getattr(self, field, None) for field in all_together]):
            raise ValidationError({'url':['Security fields must all be null or filled together.',]})

        try:
            client=self.get_client()
        except Exception as e:
            raise ValidationError({'url':['Could not establish initial connection to server. '+str(e),]})
        finally:
            client.safe_disconnect()
                   
    def save(self, *args, **kwargs):
        self.validate()
        super(Endpoint, self).save(*args, **kwargs)

    def __str__(self):
        return " : ".join([str(self.id), self.url, self.owner.username, self.modified.replace(microsecond=0).isoformat(' ')])
      
class Node(models.Model):
    endpoint = models.ForeignKey(to=Endpoint,on_delete=models.CASCADE)
    nodeid = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    type = models.CharField(choices=TYPES, max_length=10)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def validate(self):
        try:
            client = self.endpoint.get_client()
        except Exception as e:
            raise ValidationError({'endpoint':['Could not establish initial connection to server. '+str(e),]})
        try:
            client.get_node(self.nodeid)
        except:
            raise ValidationError({'nodeid':['Could not establish initial connection to node. '+str(e),]})
        finally:
            client.safe_disconnect()

       
    def save(self, *args, **kwargs):
        self.validate()
        super(Node, self).save(*args, **kwargs)

    class Meta:
        unique_together= ('endpoint','nodeid')

    def __str__(self):
        return " : ".join([str(self.id), self.nodeid,self.type,str(self.endpoint), self.modified.replace(microsecond=0).isoformat(' ')])

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
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user_start = models.DateTimeField(blank=True, null=True)
    user_end = models.DateTimeField(blank=True, null=True)
    data_start = computed_property.ComputedDateTimeField(compute_from="get_data_start",blank=True,null=True)
    data_end = computed_property.ComputedDateTimeField(compute_from="get_data_end",blank=True,null=True)
    start = computed_property.ComputedDateTimeField(compute_from="get_start",blank=True,null=True)
    end = computed_property.ComputedDateTimeField(compute_from="get_end",blank=True,null=True)


    def get_timestamps(self):
        c = list(self.class_batch.values_list("timestamp",flat=True))
        v = list(self.variable_batch.values_list("timestamp",flat=True))
        e = list(self.event_batch.values_list("timestamp",flat=True))
        return set(c+v+e)

    def get_data_start(self):
        return minNum(self.get_timestamps())
         
    def get_data_end(self):
        return maxNum(self.get_timestamps())

    def get_start(self):
        return minNum([self.data_start,self.user_start])

    def get_end(self):
        return maxNum([self.data_end,self.user_end])   
    
    
    class Meta:
        unique_together=('process','name')
        verbose_name_plural = "Batches"

    def __str__(self):
        return " : ".join([str(self.id), self.name, self.process.name, self.modified.replace(microsecond=0).isoformat(' ')])

class Variable(models.Model):
    batch = models.ForeignKey('Batch',on_delete=models.CASCADE,related_name="variable_batch")
    name = models.CharField(max_length=25)
    timestamp = models.DateTimeField()
    value = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    elapsed = computed_property.ComputedFloatField(compute_from='get_elapsed',blank=True,null=True)
    
    def get_elapsed(self):
        return deltaEpoch(self.timestamp,self.batch.start)

    class Meta:
        unique_together=('batch','name','timestamp')
    
    objects = DataFrameManager()

    def __str__(self):
        return " : ".join([str(self.id), self.batch.process.name, self.batch.name, self.name, str(self.value), self.timestamp.replace(microsecond=0).isoformat(), self.modified.replace(microsecond=0).isoformat(' ')])

class Event(models.Model):
    batch = models.ForeignKey('Batch',on_delete=models.CASCADE,related_name="event_batch")
    name = models.CharField(max_length=25)
    timestamp = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    value = computed_property.ComputedBooleanField(compute_from='get_value')
    elapsed = computed_property.ComputedFloatField(compute_from='get_elapsed',blank=True,null=True)

    def get_value(self):
        return True

    def get_elapsed(self):
        return deltaEpoch(self.timestamp,self.batch.start)
      
    class Meta:
        unique_together=('batch','name','timestamp')

    objects = DataFrameManager()

    def __str__(self):
        return " : ".join([str(self.id), self.batch.process.name, self.batch.name, self.name, self.timestamp.replace(microsecond=0).isoformat(), self.modified.replace(microsecond=0).isoformat(' ')])
   
class Class(models.Model):
    batch = models.ForeignKey('Batch',on_delete=models.CASCADE,related_name="class_batch")
    name = models.CharField(max_length=25)
    value = models.CharField(max_length=25)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    timestamp = computed_property.ComputedDateTimeField(compute_from='get_elapsed',blank=True,null=True)
    elapsed = computed_property.ComputedFloatField(compute_from='get_elapsed',blank=True,null=True)
    
    def get_elapsed(self):
        return None

    class Meta:
        unique_together=('batch','name')
        verbose_name_plural = "Classes"

    objects = DataFrameManager()

    def __str__(self):
        return " : ".join([str(self.id), self.batch.process.name, self.batch.name, self.name, self.value, self.modified.replace(microsecond=0).isoformat(' ')])

