"""BioPy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from BioPyApp import views
from BioPyApp.models import Variable, Event, Class


urlpatterns = [

    path('',views.HomePageView.as_view(),name="index"),

    path('home/',views.HomeView.as_view(),name="home"),

    path('contacts/',include('contact_form.urls')),
    
    path('terms/',views.TermsView.as_view(),name="terms"),

    path('about/',views.AboutView.as_view(),name="about"),

    path('goodbye/',views.GoodbyeView.as_view(),name="goodbye"),

    path('admin/', admin.site.urls,name="admin"),

    path('accounts/', include('allauth.urls')),

    # Newletter

    path('newsletter/',include('newsletter.urls')),

    # Actions
    path('actions/',views.ActionsView.as_view()),
    
    ## Data acquisition
    path('actions/acquisition/',views.AcquisitionView.as_view()),

    ### Real-time OPCUA

    ### Historian OPCUA

    ### Remote Databases

    ### Import Files
    path('actions/acquisition/import/',views.ImportView.as_view()),
    path('actions/acquisition/import/variables/', views.FileImport.as_view(model=Variable)),
    path('actions/acquisition/import/variables/processing/', views.FileImportProcessing.as_view(model=Variable)),
    path('actions/acquisition/import/events/', views.FileImport.as_view(model=Event)),
    path('actions/acquisition/import/events/processing/', views.FileImportProcessing.as_view(model=Event)),
    path('actions/acquisition/import/classes/', views.FileImport.as_view(model=Class)),
    path('actions/acquisition/import/classes/processing/', views.FileImportProcessing.as_view(model=Class)),








    # API
    ## Real-time
   
    path('endpoints/',views.EndpointList.as_view()),
    path('endpoints/<pk>/', views.EndpointDetail.as_view()),

    path('nodes/',views.NodeList.as_view()),
    path('nodes/<pk>/', views.NodeDetail.as_view()),

    ## Historian

    path('processes/', views.ProcessList.as_view()),

    path('processes/<pk>/', views.ProcessDetail.as_view()),

    path('batches/', views.BatchList.as_view()),

    path('batches/<pk>/', views.BatchDetail.as_view()),

    path('variables/', views.VariableList.as_view()),

    path('variables/<pk>/', views.VariableDetail.as_view()),

    path('events/', views.EventList.as_view()),

    path('events/<pk>/', views.EventDetail.as_view()),

    path('classes/', views.ClassList.as_view()),

    path('classes/<pk>/', views.ClassDetail.as_view()),
]
