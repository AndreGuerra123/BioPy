from .models import Batch, Class, Endpoint, Event, Node, Process, Variable
from django.contrib.auth.models import User
#from django.core import serializers
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from urllib.parse import urlparse

### Serializer Fields ###

class OwnerSerializerField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user = self.context['request'].user
        if user.is_superuser:
            return User.objects.all()
        else:
            return User.objects.filter(username=user.username)

class ProcessSerializerField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user = self.context['request'].user
        if user.is_superuser:
            return Process.objects.all()
        else:
            return Process.objects.filter(owner=user)

class BatchSerializerField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user = self.context['request'].user
        if user.is_superuser:
            return Batch.objects.all()
        else:
            return Batch.objects.filter(process__owner=user)

class EndpointSerializerField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user = self.context['request'].user
        if user.is_superuser:
            return Endpoint.objects.all()
        else:
            return Endpoint.objects.filter(endpoint__owner=user)


### Serializers ###            
class EndpointSerializer(serializers.ModelSerializer):
    owner=OwnerSerializerField()
    class Meta:
        model = Endpoint
        fields = "__all__"

    def validate_url(self,value):
        owner = self.get_initial().get('owner')
        existing = [ep.url for ep in Endpoint.objects.filter(owner=owner)]
        if not self.unique_url(value,existing):
            raise ValidationError('Endpoint url must an unique hostname, port and path combination per user.')
        return value

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

        

class NodeSerializer(serializers.ModelSerializer):
    endpoint = EndpointSerializerField()
    class Meta:
        model = Node
        fields = "__all__"

class ProcessSerializer(serializers.ModelSerializer):
    owner=OwnerSerializerField()
    class Meta:
        model = Process
        fields = '__all__'

class BatchSerializer(serializers.ModelSerializer):
    process=ProcessSerializerField()
    class Meta:
        model = Batch
        fields = '__all__'

class VariableSerializer(serializers.ModelSerializer):
    batch=BatchSerializerField()
    class Meta:
        model = Variable
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    batch=BatchSerializerField()
    class Meta:
        model = Event
        fields = '__all__'

class ClassSerializer(serializers.ModelSerializer):
    batch=BatchSerializerField()
    class Meta:
        model = Class
        fields = '__all__'


