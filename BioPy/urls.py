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

    path('message/<pop>/',views.MessageView.as_view(),name="message"),

    # Newletter

    path('newsletter/',include('newsletter.urls')),

    # Actions
    path('actions/',views.ActionsView.as_view(),name="actions"),
    
    ## Input
    path('actions/input/',views.InputView.as_view(),name="input"),

    ### Real-time OPCUA
    path('actions/input/realtime/',views.ImportView.as_view(),name="realtime"),

    ### Historian OPCUA
    path('actions/input/historian/',views.HistorianImporterView.as_view(),name="historian"),
    path('actions/input/historian/variables/',views.VariableHistorianImporterView.as_view(),name="historian_variables"),
    path('actions/input/historian/events/',views.EventHistorianImporterView.as_view(),name="historian_events"),
    path('actions/input/historian/classes/',views.ClassHistorianImporterView.as_view(),name="historian_classes"),

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
    path('actions/output/dataframe/',views.DataframeView.as_view(),name="df"),
    
    path('actions/output/dataframe/single/',views.SingleProcessDataframeView.as_view(),name="sp_df"),
    
    path('actions/output/dataframe/single/variable/',views.VariableSingleProcessDataframeView.as_view(),name="v_sp_df"),
    path('actions/output/dataframe/single/variable/download/',views.VariableSingleProcessDataframeDownloadView.as_view(),name="d_v_sp_df"),
    
    path('actions/output/dataframe/single/event/',views.EventSingleProcessDataframeView.as_view(),name="e_sp_df"),
    path('actions/output/dataframe/single/event/download/',views.EventSingleProcessDataframeDownloadView.as_view(),name="d_e_sp_df"),

    path('actions/output/dataframe/single/variable/',views.ClassSingleProcessDataframeView.as_view(),name="c_sp_df"),
    path('actions/output/dataframe/single/class/download/',views.ClassSingleProcessDataframeDownloadView.as_view(),name="d_c_sp_df"),

    path('actions/output/dataframe/multi/',views.MultiProcessDataframeView.as_view(),name="mp_df"),

    path('actions/output/dataframe/multi/variable/',views.VariableMultiProcessDataframeView.as_view(),name="v_mp_df"),
    path('actions/output/dataframe/multi/event/',views.EventMultiProcessDataframeView.as_view(),name="e_mp_df"),
    path('actions/output/dataframe/multi/class/',views.ClassMultiProcessDataframeView.as_view(),name="c_mp_df"),

    # ###Export data
    path('actions/output/export/',views.ExportView.as_view(),name="export"),
    path('actions/output/export/variables/', views.VariableFileExport.as_view(),name="export_variables"),
    path('actions/output/export/events/', views.EventFileExport.as_view(),name="export_events"),
    path('actions/output/export/classes/', views.ClassFileExport.as_view(),name="export_classes"),
    
    ## View
    path('actions/view/',views.ViewView.as_view(),name="view"),

    ## Configure
    path('actions/configure/',views.ConfigureView.as_view(),name="configure"),
    path('actions/configure/connections',views.ConnectionsWizardView.as_view(),name="configure_connections"),
    path('actions/configure/structure',views.StructureWizardView.as_view(),name="configure_structure"),


    # API
    ## Real-time
    path('endpoints/',views.EndpointList.as_view(),name="endpoints_list"),
    path('endpoints/create/',views.EndpointCreate.as_view(),name="create_endpoint"),
    path('endpoints/update/<pk>/',views.EndpointUpdate.as_view(),name="update_endpoint"),
    path('endpoints/delete/<pk>/',views.EndpointDelete.as_view(),name="delete_endpoint"),
    path('endpoints/<pk>/', views.EndpointDetail.as_view()),

    path('nodes/',views.NodeList.as_view(),name="nodes_list"),
    path('nodes/create/',views.NodeCreate.as_view(),name="create_node"),
    path('nodes/update/<pk>/',views.NodeUpdate.as_view(),name="update_node"),
    path('nodes/delete/<pk>/',views.NodeDelete.as_view(),name="delete_node"),
    path('nodes/<pk>/', views.NodeDetail.as_view()),

    ## Historian
    path('processes/', views.ProcessList.as_view(),name="processes_list"),
    path('processes/create/',views.ProcessCreate.as_view(),name="create_process"),
    path('processes/update/<pk>/',views.ProcessUpdate.as_view(),name="update_process"),
    path('processes/delete/<pk>/',views.ProcessDelete.as_view(),name="delete_process"),
    path('processes/<pk>/', views.ProcessDetail.as_view()),

    path('batches/', views.BatchList.as_view(),name="batches_list"),
    path('batches/create/',views.BatchCreate.as_view(),name="create_batch"),
    path('batches/update/<pk>/',views.BatchUpdate.as_view(),name="update_batch"),
    path('batches/delete/<pk>/',views.BatchDelete.as_view(),name="delete_batch"),
    path('batches/<pk>/', views.BatchDetail.as_view()),

    path('variables/', views.VariableList.as_view(),name="variables_list"),
    path('variables/create/',views.VariableCreate.as_view(),name="create_variable"),
    path('variables/update/<pk>/',views.VariableUpdate.as_view(),name="update_variable"),
    path('variables/delete/<pk>/',views.VariableDelete.as_view(),name="delete_variable"),
    path('variables/<pk>/', views.VariableDetail.as_view()),

    path('events/', views.EventList.as_view(),name="events_list"),
    path('events/create/',views.EventCreate.as_view(),name="create_event"),
    path('events/update/<pk>/',views.EventUpdate.as_view(),name="update_event"),
    path('events/delete/<pk>/',views.EventDelete.as_view(),name="delete_event"),
    path('events/<pk>/', views.EventDetail.as_view()),

    path('classes/', views.ClassList.as_view(),name="classes_list"),
    path('classes/create/',views.ClassCreate.as_view(),name="create_class"),
    path('classes/update/<pk>/',views.ClassUpdate.as_view(),name="update_class"),
    path('classes/delete/<pk>/',views.ClassDelete.as_view(),name="delete_class"),
    path('classes/<pk>/', views.ClassDetail.as_view()),
]
