from .models import Process, Batch, Variable, Event, Class
from .serializers import UserSerializer, RegistrationSerializer, ProcessSerializer, BatchSerializer, VariableSerializer, EventSerializer, ClassSerializer
from rest_framework import generics
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import views as auth_views

#For registration only
from django.views import generic

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

class ContactsView(generic.TemplateView):
    template_name = 'contacts.html'

class TermsView(generic.TemplateView):
    template_name = 'terms.html'

# General

@method_decorator(login_required, name='dispatch')
class ProcessList(generics.ListCreateAPIView):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    
@method_decorator(login_required, name='dispatch')
class ProcessDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
@method_decorator(login_required, name='dispatch')
class BatchList(generics.ListCreateAPIView):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer

@method_decorator(login_required, name='dispatch')
class BatchDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer

@method_decorator(login_required, name='dispatch')
class VariableList(generics.ListCreateAPIView):
    queryset = Variable.objects.all()
    serializer_class = VariableSerializer

@method_decorator(login_required, name='dispatch')    
class VariableDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Variable.objects.all()
    serializer_class = VariableSerializer

@method_decorator(login_required, name='dispatch')
class EventList(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

@method_decorator(login_required, name='dispatch')
class EventDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    
@method_decorator(login_required, name='dispatch')
class ClassList(generics.ListCreateAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
        

@method_decorator(login_required, name='dispatch')
class ClassDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    

