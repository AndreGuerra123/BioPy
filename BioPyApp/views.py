from .models import Batch, Class, Configuration, Endpoint, Event, Node, \
    Process, Server, Variable, Node
from .permissions import hasBatchPermission, hasConfigurationPermission, \
    hasDataPermission, hasEndpointPermission, hasNodePermission, \
    hasProcessPermission, hasServerPermission
from .serializers import BatchSerializer, ClassSerializer, \
    ConfigurationSerializer, EndpointSerializer, EventSerializer, \
    NodeSerializer, ProcessSerializer, ServerSerializer, VariableSerializer
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import generic
from rest_framework import generics


# Universal

@method_decorator(login_required, name='dispatch')
class HomeView(generic.TemplateView):
    template_name = 'home.html'

class GoodbyeView(generic.TemplateView):
    template_name = 'goodbye.html'

class HomePageView(generic.TemplateView):
    template_name = "homepage.html"

class AboutView(generic.TemplateView):
    template_name = 'about.html' 

class TermsView(generic.TemplateView):
    template_name = 'terms.html'

# Model views

#Real-time
@method_decorator(login_required,name='dispatch')
class ServerList(generics.ListCreateAPIView):
    """
        Create new OPCUA Server instances and visualize existing ones.
    """
    serializer_class = ServerSerializer
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Server.objects.all()
        else:
            return Server.objects.filter(owner=user)

@method_decorator(login_required, name='dispatch')
class ServerDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Visualize and modify an existing OPCUA Server instance.
    """
    serializer_class = ServerSerializer
    permission_classes = [hasServerPermission]
    queryset = Server.objects.all()


@method_decorator(login_required,name='dispatch')
class EndpointList(generics.ListCreateAPIView):
    """
        Create new OPCUA Endpoint instances and visualize existing ones.
    """
    serializer_class = EndpointSerializer
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Endpoint.objects.all()
        else:
            return Endpoint.objects.filter(server__owner=user)

@method_decorator(login_required, name='dispatch')
class EndpointDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Visualize and modify an existing OPCUA Endpoint instance.
    """
    serializer_class = EndpointSerializer
    permission_classes = [hasEndpointPermission]
    queryset = Endpoint.objects.all()


@method_decorator(login_required,name='dispatch')
class ConfigurationList(generics.ListCreateAPIView):
    """
        Create new OPCUA Configuration instances and visualize existing ones.
    """
    serializer_class = ConfigurationSerializer
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Configuration.objects.all()
        else:
            return Configuration.objects.filter(endpoint__server__owner=user)

@method_decorator(login_required, name='dispatch')
class ConfigurationDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Visualize and modify an existing OPCUA Configuration instance.
    """
    serializer_class = ConfigurationSerializer
    permission_classes = [hasConfigurationPermission]
    queryset = Configuration.objects.all()

@method_decorator(login_required,name='dispatch')
class NodeList(generics.ListCreateAPIView):
    """
        Create new OPCUA Node instances and visualize existing ones.
    """
    serializer_class = NodeSerializer
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Node.objects.all()
        else:
            return Node.objects.filter(configuration__endpoint__server__owner=user)

@method_decorator(login_required, name='dispatch')
class NodeDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Visualize and modify an existing OPCUA Node instance.
    """
    serializer_class = NodeSerializer
    permission_classes = [hasNodePermission]
    queryset = Node.objects.all()

## Historian

@method_decorator(login_required, name='dispatch')
class ProcessList(generics.ListCreateAPIView):
    """
        Create new Process instances and visualize existing ones.
    """
    serializer_class = ProcessSerializer
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Process.objects.all()
        else:
            return Process.objects.filter(owner=user)
    
@method_decorator(login_required, name='dispatch')
class ProcessDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Visualize and modify an existing Process instance.
    """
    serializer_class = ProcessSerializer
    permission_classes = [hasProcessPermission]
    queryset = Process.objects.all()

@method_decorator(login_required, name='dispatch')
class BatchList(generics.ListCreateAPIView):
    """
        Create new Batch instances and visualize existing ones.
    """
    serializer_class = BatchSerializer
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Batch.objects.all()
        else:
            return Batch.objects.filter(process__owner=user)

@method_decorator(login_required, name='dispatch')
class BatchDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Visualize and modify an existing Batch instance.
    """
    serializer_class = BatchSerializer
    permission_classes = [hasBatchPermission]
    queryset = Batch.objects.all()

@method_decorator(login_required, name='dispatch')
class VariableList(generics.ListCreateAPIView):
    """
        Create new Variable instances and visualize existing ones.
    """
    serializer_class = VariableSerializer
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Variable.objects.all()
        else:
            return Variable.objects.filter(batch__process__owner=user)

@method_decorator(login_required, name='dispatch')    
class VariableDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Visualize and modify an existing Variable instance.
    """
    serializer_class = VariableSerializer
    permission_classes = [hasDataPermission]
    queryset = Variable.objects.all()

@method_decorator(login_required, name='dispatch')
class EventList(generics.ListCreateAPIView):
    """
        Create new Event instances and visualize existing ones.
    """
    serializer_class = EventSerializer
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Event.objects.all()
        else:
            return Event.objects.filter(batch__process__owner=user)

@method_decorator(login_required, name='dispatch')
class EventDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Visualize and modify an existing Event instance.
    """
    serializer_class = EventSerializer
    permission_classes = [hasDataPermission]
    queryset = Event.objects.all()
    
@method_decorator(login_required, name='dispatch')
class ClassList(generics.ListCreateAPIView):
    """
        Create new Class instances and visualize existing ones.
    """
    serializer_class = ClassSerializer
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Class.objects.all()
        else:
            return Class.objects.filter(batch__process__owner=user)
        
@method_decorator(login_required, name='dispatch')
class ClassDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Visualize and modify an existing Class instance.
    """
    serializer_class = ClassSerializer
    permission_classes = [hasDataPermission]
    queryset = Class.objects.all()
    

