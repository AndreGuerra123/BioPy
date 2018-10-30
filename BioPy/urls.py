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
    path('actions/',views.ActionsView.as_view(),name="actions"),
    
    ## Input
    path('actions/input/',views.InputView.as_view(),name="input"),

    ### Real-time OPCUA
    path('actions/input/realtime/',views.ImportView.as_view(),name="realtime"),

    ### Historian OPCUA
    path('actions/input/historian/',views.HistorianWizardView.as_view(),name="historian"),
    #path('actions/input/historian/importer/<data>/',views.historian_importer,name="historian_importer"),
    #path('actions/input/historian/processor/<data>/',views.historian_processor,name="historian_processor"),

    ### Import Files
    path('actions/input/import/',views.ImportView.as_view(),name="import"),
    path('actions/input/import/variables/', views.VariableFileImport.as_view(),name="import_variables"),
    path('actions/input/import/variables/processing/', views.VariableFileImportProcessing.as_view(),name="import_variables_processing"),
    path('actions/input/import/events/', views.EventFileImport.as_view(),name="import_events"),
    path('actions/input/import/events/processing/', views.EventFileImportProcessing.as_view(),name="import_events_processing"),
    path('actions/input/import/classes/', views.ClassFileImport.as_view(),name="import_classes"),
    path('actions/input/import/classes/processing/', views.ClassFileImportProcessing.as_view(),name="import_classes_processing"),

    ## Output
    path('actions/output/',views.OutputView.as_view(),name="output"),

    ###Dataframes
    path('actions/output/dataset/',views.DatasetView.as_view(),name="dataset"),
    # path('actions/output/dataset/tensor/', views.VariableDataframe.as_view(),name="dataframe_variables"),
    # Alltypes
    # path('actions/output/dataset/dataframes/', views.EventDataframe.as_view(),name="dataframe_events"),
    # ALltypes
    
    # ###Export data
    path('actions/output/export/',views.ExportView.as_view(),name="export"),
    path('actions/output/export/variables/', views.VariableFileExport.as_view(),name="export_variables"),
    path('actions/output/export/events/', views.EventFileExport.as_view(),name="export_events"),
    path('actions/output/export/classes/', views.ClassFileExport.as_view(),name="export_classes"),
    
    path('actions/output/export/',views.ViewView.as_view(),name="view"),


    # API
    ## Real-time
   
    path('endpoints/',views.EndpointList.as_view(),name="endpoints_list"),
    path('endpoints/<pk>/', views.EndpointDetail.as_view()),

    path('nodes/',views.NodeList.as_view(),name="nodes_list"),
    path('nodes/<pk>/', views.NodeDetail.as_view()),

    ## Historian

    path('processes/', views.ProcessList.as_view(),name="processes_list"),

    path('processes/<pk>/', views.ProcessDetail.as_view()),

    path('batches/', views.BatchList.as_view(),name="batches_list"),

    path('batches/<pk>/', views.BatchDetail.as_view()),

    path('variables/', views.VariableList.as_view(),name="variables_list"),

    path('variables/<pk>/', views.VariableDetail.as_view()),

    path('events/', views.EventList.as_view(),name="events_list"),

    path('events/<pk>/', views.EventDetail.as_view()),

    path('classes/', views.ClassList.as_view(),name="classes_list"),

    path('classes/<pk>/', views.ClassDetail.as_view()),
]
