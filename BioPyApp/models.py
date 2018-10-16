from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms.models import InlineForeignKeyField
from opcua.ua.ua_binary import nodeid_from_binary

class Server(models.Model):
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    host = models.CharField(null=False,blank=False,max_length=100)
    port = models.PositiveIntegerField(null=False,blank=False,validators=[MinValueValidator(1024),MaxValueValidator(65535)])
    username = models.CharField(null=True,blank=True,max_length=100)
    password = models.CharField(null=True,blank=True,max_length=100)
    certificate = models.FileField(blank=True,null=True)
    privatekey = models.FileField(blank=True,null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('owner','host','port')

class Endpoint(models.Model):
    server = models.ForeignKey(to=Server,on_delete=models.CASCADE)
    url = models.CharField(unique=True, max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('server','url')

class Configuration(models.Model):
    endpoint = models.ManyToManyField(to=Endpoint)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

class Node(models.Model):
    TYPES=[("variable","Variable"),("classsifier","Classifier"),("event","Event"),("spectrum","Spectrum")]
    configuration = models.ForeignKey(to=Configuration,on_delete=models.CASCADE)
    nodeid = models.CharField(max_length=100)
    type = models.CharField(choices=TYPES, max_length=10)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together= ('configuration','nodeid')

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
    date = models.DateTimeField()
    value = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return " : ".join([str(self.id), self.batch.process.name, self.batch.name, self.name, str(self.value), self.date.replace(microsecond=0).isoformat(), self.modified.replace(microsecond=0).isoformat(' ')])

class Event(models.Model):
    batch = models.ForeignKey('Batch',on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    date = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return " : ".join([str(self.id), self.batch.process.name, self.batch.name, self.name, self.date.replace(microsecond=0).isoformat(), self.modified.replace(microsecond=0).isoformat(' ')])
   
class Class(models.Model):
    batch = models.ForeignKey('Batch',on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    value = models.CharField(max_length=25)
    prior = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name_plural = "Classes"

       
    def __str__(self):
        return " : ".join([str(self.id), self.batch.process.name, self.batch.name, self.name, srt(self.value),self.date.replace(microsecond=0).isoformat(), self.modified.replace(microsecond=0).isoformat(' ')])

