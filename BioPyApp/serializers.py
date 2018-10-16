from .models import Batch, Class, Configuration, Endpoint, Event, Node, \
    Process, Server, Variable
from django.contrib.auth.models import User
from django.core import serializers
from rest_framework import serializers


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

class ServerSerializerField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user = self.context['request'].user
        if user.is_superuser:
            return Server.objects.all()
        else:
            return Server.objects.filter(owner=user)

class EndpointSerializerField(serializers.PrimaryKeyRelatedField):
    many=True
    def get_queryset(self):
        user = self.context['request'].user
        if user.is_superuser:
            return Endpoint.objects.all()
        else:
            return Endpoint.objects.filter(server__owner=user)

class ConfigurationSerializerField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user = self.context['request'].user
        if user.is_superuser:
            return Configuration.objects.all()
        else:
            return Configuration.objects.filter(endpoint__server__owner=user)

### Serializers ###            

class ServerSerializer(serializers.ModelSerializer):
    owner=OwnerSerializerField()
    class Meta:
        model = Server
        fields = "__all__"

class EndpointSerializer(serializers.ModelSerializer):
    server=ServerSerializerField()
    class Meta:
        model = Endpoint
        fields = "__all__"

class ConfigurationSerializer(serializers.ModelSerializer):
    endpoint=EndpointSerializerField()
    class Meta:
        model = Configuration
        fields = "__all__"

class NodeSerializer(serializers.ModelSerializer):
    configuration = ConfigurationSerializerField()
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


