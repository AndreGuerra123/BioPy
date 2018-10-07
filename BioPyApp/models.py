from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

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
    end = models.DateTimeField(blank=True)
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

