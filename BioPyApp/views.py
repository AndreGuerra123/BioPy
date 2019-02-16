import tempfile
import os
from builtins import getattr
from datetime import datetime

import numpy as np
import pandas as pd
from BioPyApp.forms import connection, dataframe, historian, structure
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.html import escape, escapejs
from django.utils.translation import gettext as _
from django.views import generic
from django_addanother.views import CreatePopupMixin, UpdatePopupMixin
from formtools.wizard.views import SessionWizardView
from import_export.formats.base_formats import DEFAULT_FORMATS, JSON
from import_export.forms import ConfirmImportForm, ExportForm, ImportForm
from import_export.resources import RowResult, modelresource_factory
from import_export.tmp_storages import TempFolderStorage
from rest_framework import generics
from rest_framework.generics import CreateAPIView
from rest_framework.reverse import reverse_lazy

from BioPyApp.mixins import DataframeDownload, SingleProcessDataframeFormView, \
    SingleProcessDataframeMixin, HistorianImporterFormView
from BioPyApp.models import Batch, Class, Endpoint, Event, Node, Process, \
    Variable
from BioPyApp.permissions import hasBatchPermission, hasDataPermission, \
    hasEndpointPermission, hasNodePermission, hasProcessPermission
from BioPyApp.resources import ClassResource, EventResource, VariableResource
from BioPyApp.serializers import BatchSerializer, ClassSerializer, \
    EndpointSerializer, EventSerializer, NodeSerializer, ProcessSerializer, \
    VariableSerializer
from BioPyApp.widgets import DeletePopupMixin
from BioPyApp.mixins import HistorianImporterFormView
from BioPyApp.drivers.historian import OPCUAVariableHistorianDataset

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

## Input Data
@method_decorator(login_required,name='dispatch')
class InputView(generic.TemplateView):
    template_name = 'input/input.html'

### Realtime


### Historian Importer
def historian_importer(request,resource,dataset,template):
    context = {}
    if request.POST:
        result = resource.import_data(dataset, dry_run=True,raise_errors=False,file_name=tmp_storage.name,user=request.user)
        context['result'] = result
        if not result.has_errors():
            tmp_storage = TempFolderStorage()
            input_format=JSON
            tmp_storage.save(dataset.export('json').encode(),input_format.get_read_mode)
            context['confirm_form'] = ConfirmImportForm(initial={
            'import_file_name': tmp_storage.name,
            'original_file_name': tmp_storage.name,
            'input_format':input_format
            })

    context['fields'] = [f.column_name for f in resource.get_user_visible_fields()]
    return TemplateResponse(request, [template],context)

def historian_processor(request,resource,redirect_url):

    confirm_form = ConfirmImportForm(request.POST)
    if confirm_form.is_valid():
        input_format = JSON
        tmp_storage = TempFolderStorage(name=confirm_form.cleaned_data['import_file_name'])
        data = tmp_storage.read(input_format.get_read_mode())
        dataset = input_format.create_dataset(data)
        resource.import_data(dataset,
                                    dry_run=False,
                                    raise_errors=True,
                                    file_name=confirm_form.cleaned_data['original_file_name'],
                                    user=request.user)
        tmp_storage.remove()
        return HttpResponseRedirect(reverse_lazy(redirect_url))

@method_decorator(login_required,name="dispatch")
class HistorianImporterView(generic.TemplateView):
    template_name = "input/historian/historian.html"

@method_decorator(login_required,name="dispatch")
class VariableHistorianImporterView(HistorianImporterFormView):
    model = Variable
    form_list = [
        ("step_one", structure.SelectProcessForm),
        ("step_two", structure.SelectBatchForm),
        ("step_three", historian.StartEndForm),
        ("step_four", connection.SelectMultipleEndpointsForm),
        ("step_five", connection.SelectMultipleVariableNodesForm),
        ]

    def done(self,form_list,**kwargs):
        params={}
        for form in form_list:
            params.update(form.cleaned_data)
        resource = VariableResource(self.request.user)
        dataset = OPCUAVariableHistorianDataset(params)
        template = 'input/historian/historian_importer.html'
        return historian_importer(self.request,resource,dataset,template)

@method_decorator(login_required,name="dispatch")
class EventHistorianImporterView(HistorianImporterFormView):
    model = Event
    form_list = [
        ("step_one", structure.SelectProcessForm),
        ("step_two", structure.SelectBatchForm),
        ("step_three", historian.StartEndForm),
        ("step_four", connection.SelectMultipleEndpointsForm),
        ("step_five", connection.SelectMultipleEventNodesForm),
        ]

    def done(self,form_list,**kwargs):
        params={}
        for form in form_list:
            params.update(form.cleaned_data)
        resource = VariableResource(self.request.user)
        dataset = OPCUAVariableHistorianDataset(params)
        template = 'input/historian/historian_importer.html'
        return historian_importer(self.request,resource,dataset,template)
@method_decorator(login_required,name="dispatch")
class ClassHistorianImporterView(HistorianImporterFormView):
    model = Class
    form_list = [
        ("step_one", structure.SelectProcessForm),
        ("step_two", structure.SelectBatchForm),
        ("step_three", historian.StartEndForm),
        ("step_four", connection.SelectMultipleEndpointsForm),
        ("step_five", connection.SelectMultipleClassNodesForm),
        ]
    def done(self,form_list,**kwargs):
        params={}
        for form in form_list:
            params.update(form.cleaned_data)
        resource = VariableResource(self.request.user)
        dataset = OPCUAVariableHistorianDataset(params)
        template = 'input/historian/historian_importer.html'
        return historian_importer(self.request,resource,dataset,template)
 

### Import Files

def importer(request,resource,template):
    '''
    Perform a dry_run of the import to make sure the import will not
    result in errors.  If there where no error, save the user
    uploaded file to a local temp file that will be used by
    'process_import' for the actual import.
    '''
    from_encoding = "utf-8"   
    context = {}
    import_formats = [f for f in DEFAULT_FORMATS if f().can_import()]
    form = ImportForm(import_formats,request.POST or None,request.FILES or None)

    if request.POST and form.is_valid():
        input_format = import_formats[int(form.cleaned_data['input_format'])]()
        import_file = form.cleaned_data['import_file']
        tmp_storage = TempFolderStorage()
            
        try:
            #save
            data = bytes()
            for chunk in import_file.chunks():
                data += chunk
            tmp_storage.save(data, input_format.get_read_mode())
                
            #read
            data = tmp_storage.read(input_format.get_read_mode())

            #decoding
            if not input_format.is_binary() and from_encoding:
                data = force_text(data, from_encoding)

            #dataset    
            dataset = input_format.create_dataset(data)
            
        except UnicodeDecodeError as e:
            return HttpResponse (_(u"<h1>Imported file has a wrong encoding: %s</h1>" % e))
        except Exception as e:
            return HttpResponse(_(u"<h1>%s encountered while trying to load or the read file: %s</h1>" % (type(e).__name__, import_file.name)))
        print(dataset)
        result = resource.import_data(dataset, dry_run=True,
                                          raise_errors=False,
                                          file_name=import_file.name,
                                          user=request.user)
        context['result'] = result
        if not result.has_errors():
            context['confirm_form'] = ConfirmImportForm(initial={
            'import_file_name': tmp_storage.name,
            'original_file_name': import_file.name,
            'input_format': form.cleaned_data['input_format']
            })

    context['form'] = form
    context['fields'] = [f.column_name for f in resource.get_user_visible_fields()]
    return TemplateResponse(request, [template],context)

def processor(request,resource,template,redirect_url_name):

    from_encoding = "utf-8"

    confirm_form = ConfirmImportForm(request.POST)
    if confirm_form.is_valid():
        import_formats = [f for f in DEFAULT_FORMATS if f().can_import()]
        input_format = import_formats[int(confirm_form.cleaned_data['input_format'])]()
        tmp_storage = TempFolderStorage(name=confirm_form.cleaned_data['import_file_name'])
        data = tmp_storage.read(input_format.get_read_mode())
        if not input_format.is_binary() and from_encoding:
            data = force_text(data, from_encoding)
        dataset = input_format.create_dataset(data)
        resource.import_data(dataset,
                                    dry_run=False,
                                    raise_errors=True,
                                    file_name=confirm_form.cleaned_data['original_file_name'],
                                    user=request.user)
        tmp_storage.remove()
        return HttpResponseRedirect(reverse_lazy(redirect_url_name))

@method_decorator(login_required,name='dispatch')
class ImportView(generic.TemplateView):
    template_name = 'input/import/import.html'

#### VariableFileImport
@method_decorator(login_required, name="dispatch") 
class VariableFileImport(generic.View):
    def get(self,*args, **kwargs):
        return importer(
            self.request,
            VariableResource(self.request.user),
            'input/import/variable_file_import.html')

    def post(self,*args,**kwargs):
        return importer(
            self.request,
            VariableResource(self.request.user),
            'input/import/variable_file_import.html')

#### VariableFileProcessingImport
@method_decorator(login_required,name='dispatch')
class VariableFileImportProcessing(generic.View):
    def post(self,*args,**kwargs):
        return processor(
            self.request,
            VariableResource(self.request.user),
            'input/import/variable_file_import.html',
            'variables_list')    
        
#### EventFileImport   
@method_decorator(login_required,name='dispatch')
class EventFileImport(generic.TemplateView):
    def get(self,*args, **kwargs):
        return importer(
            self.request,
            EventResource(self.request.user),
            'input/import/event_file_import.html')

    def post(self,*args,**kwargs):
        return importer(
            self.request,
            EventResource(self.request.user),
            'input/import/event_file_import.html')

#### EventFileProcessingImport
@method_decorator(login_required,name='dispatch')
class EventFileImportProcessing(generic.View):
    def post(self,*args,**kwargs):
        return processor(
            self.request,
            EventResource(self.request.user),
            'input/import/event_file_import.html',
            'events_list')

#### ClassFileImport   
@method_decorator(login_required,name='dispatch')
class ClassFileImport(generic.View):
    def get(self,*args, **kwargs):
        return importer(
            self.request,
            ClassResource(self.request.user),
            'input/import/class_file_import.html')

    def post(self,*args,**kwargs):
        return importer(
            self.request,
            ClassResource(self.request.user),
            'input/import/class_file_import.html')

#### ClassFileProcessingImport
@method_decorator(login_required,name='dispatch')
class ClassFileImportProcessing(generic.View):
    def post(self,*args,**kwargs):
        return processor(
            self.request,
            ClassResource(self.request.user),
            'input/import/class_file_import.html',
            'classes_list')  

## Output Data
@method_decorator(login_required,name='dispatch')
class OutputView(generic.TemplateView):
    template_name = 'output/output.html'

def exporter(request,resource,template):

    context = {}
    formats = [f for f in DEFAULT_FORMATS if f().can_export()]
    form = ExportForm(formats, request.POST or None)
        
    if form.is_valid():
        file_format = formats[int(form.cleaned_data['file_format'])]()
        filename = "%s-%s.%s" % (resource._meta.model.__name__,datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),file_format.get_extension())
        data = resource.export()
        export_data = file_format.export_data(data)
        content_type = file_format.get_content_type()
        response = HttpResponse(export_data, content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename=%s' % (filename,)
        return response

    context['form'] = form
    return TemplateResponse(request,[template],context)

@method_decorator(login_required, name="dispatch") 
class VariableFileExport(generic.View):
    def get(self,*args, **kwargs):
        return exporter(self.request,
            VariableResource(self.request.user),
            'output/export/variable_file_export.html')

    def post(self,*args,**kwargs):
        return exporter(
            self.request,
            VariableResource(self.request.user),
            'output/export/variable_file_export.html')

@method_decorator(login_required, name="dispatch") 
class ClassFileExport(generic.View):
    def get(self,*args, **kwargs):
        return exporter(self.request,
            ClassResource(self.request.user),
            'output/export/class_file_export.html')

    def post(self,*args,**kwargs):
        return exporter(
            self.request,
            ClassResource(self.request.user),
            'output/export/class_file_export.html')

@method_decorator(login_required, name="dispatch") 
class EventFileExport(generic.View):
    def get(self,*args, **kwargs):
        return exporter(self.request,
            EventResource(self.request.user),
            'output/export/event_file_export.html')

    def post(self,*args,**kwargs):
        return exporter(
            self.request,
            EventResource(self.request.user),
            'output/export/event_file_export.html')

### Dataframes
@method_decorator(login_required,name='dispatch')
class DataframeView(generic.TemplateView):
    template_name = 'output/dataframe/dataframe.html'

#### Single Process
@method_decorator(login_required,name='dispatch')
class SingleProcessDataframeView(generic.TemplateView):
    template_name = 'output/dataframe/single/single.html'

@method_decorator(login_required,name='dispatch')
class VariableSingleProcessDataframeView(SingleProcessDataframeFormView):
    model = Variable
    form_list=[
        ("step_one", structure.SelectProcessForm),
        ("step_two", structure.SelectMultipleBatchesForm),
        ("step_three", dataframe.SelectVariablePredictorsForm),
        ("step_four", dataframe.SelectSingleProcessDataframeOptionsForm),
        ]
    download_url_name = 'd_v_sp_df'

@method_decorator(login_required,name='dispatch')
class VariableSingleProcessDataframeDownloadView(DataframeDownload,SingleProcessDataframeMixin):
    model = Variable

@method_decorator(login_required,name='dispatch')
class EventSingleProcessDataframeView(SingleProcessDataframeFormView):
    model = Event
    form_list=[
        ("step_one", structure.SelectProcessForm),
        ("step_two", structure.SelectMultipleBatchesForm),
        ("step_three", dataframe.SelectEventPredictorsForm),
        ("step_four", dataframe.SelectSingleProcessDataframeOptionsForm),
        ]
    download_url_name = 'd_e_sp_df'

@method_decorator(login_required,name='dispatch')
class EventSingleProcessDataframeDownloadView(DataframeDownload,SingleProcessDataframeMixin):
    model = Event

@method_decorator(login_required,name='dispatch')
class ClassSingleProcessDataframeView(SingleProcessDataframeFormView):
    model = Class
    form_list=[
        ("step_one", structure.SelectProcessForm),
        ("step_two", structure.SelectMultipleBatchesForm),
        ("step_three", dataframe.SelectClassPredictorsForm),
        ("step_four", dataframe.SelectSingleProcessDataframeOptionsForm),
        ]
    download_url_name = 'd_c_sp_df'

@method_decorator(login_required,name='dispatch')
class ClassSingleProcessDataframeDownloadView(DataframeDownload,SingleProcessDataframeMixin):
    model = Class
    
#### Multi Process
class MultiProcessDataframeView(generic.TemplateView):
    template_name = 'output/dataframe/multi/multi.html'

class VariableMultiProcessDataframeView(generic.FormView):
    pass

class EventMultiProcessDataframeView(generic.FormView):
    pass

class ClassMultiProcessDataframeView(generic.FormView):
    pass


### Export Files
@method_decorator(login_required,name='dispatch')
class ExportView(generic.TemplateView):
    template_name = 'output/export/export.html'

## View
@method_decorator(login_required,name='dispatch')
class ViewView(generic.TemplateView):
    template_name = 'view/view.html'

## Configure
@method_decorator(login_required,name='dispatch')
class ConfigureView(generic.TemplateView):
    template_name = 'configure/configure.html'

### Connections
@method_decorator(login_required,name='dispatch')
class ConnectionsWizardView(SessionWizardView):
    form_list = [
        ("step_one", connection.SelectEndpointForm),
        ("step_two", connection.SelectNodeForm),
        ]

    template_name = "configure/connections/connections.html"

    def get_form_kwargs(self, step):
        if step == 'step_one': #inputs user
            return {'user': self.request.user}
        elif step == 'step_two' : #inputs endpoint
            return {'endpoints':[self.get_cleaned_data_for_step('step_one').get('endpoint')]}
        else:
            return {}
    
    def done(self,form_list,**kwargs):
        return redirect('configure')

### Stucture
@method_decorator(login_required,name='dispatch')
class StructureWizardView(SessionWizardView):
    form_list = [
        ("step_one", structure.SelectProcessForm),
        ("step_two", structure.SelectBatchForm),
        ("step_three", structure.DataConfigurationForm)
        ]

    template_name = "configure/structure/structure.html"

    def get_form_kwargs(self, step):
        if step == 'step_one': #inputs user
            return {'user': self.request.user}
        elif step == 'step_two' : #inputs endpoint
            return {'process':self.get_cleaned_data_for_step('step_one').get('process')}
        elif step == "step_three" :
            return {'batch':self.get_cleaned_data_for_step('step_two').get('batch')}
        else:
            return {}
    
    def done(self,form_list,**kwargs):
        return redirect('configure')

# API views
class MessageView(generic.TemplateView):
    template_name = 'crud/message.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pop"] = kwargs['pop']
        return context
    
class CreateMixin(SuccessMessageMixin):
    fields = '__all__'
    template_name = 'crud/form.html'
    success_url = reverse_lazy('message',kwargs={"pop":True})
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Create"
        context["name"]=self.model.__name__
        return context

    def get_success_message(self, cleaned_data):
        return self.model.__name__+" was created successfully."

class UpdateMixin(SuccessMessageMixin):
    fields = '__all__'
    template_name = 'crud/form.html'
    success_url = reverse_lazy('message',kwargs={"pop":True})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Update"
        context["name"] = self.model.__name__
        return context

    def get_success_message(self,cleaned_data):
        return self.model.__name__+" was updated successfully."

class DeleteMixin(SuccessMessageMixin):
    fields = '__all__'
    template_name = 'crud/form.html'
    success_url = reverse_lazy('message',kwargs={"pop":True})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Delete"
        context["name"] = self.model.__name__
        return context

    def get_success_message(self,cleaned_data):
        return self.model.__name__+" was deleted successfully."

## Real-time
@method_decorator(login_required,name='dispatch')
class EndpointList(generics.ListCreateAPIView):
    """
        Create new OPCUA Server instances and visualize existing ones.
    """
    serializer_class = EndpointSerializer
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Endpoint.objects.all()
        else:
            return Endpoint.objects.filter(owner=user)

@method_decorator(login_required, name='dispatch')
class EndpointDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Visualize and modify an existing OPCUA Server instance.
    """
    serializer_class = EndpointSerializer
    permission_classes = [hasEndpointPermission]
    queryset = Endpoint.objects.all()

@method_decorator(login_required, name="dispatch")
class EndpointCreate(CreatePopupMixin,CreateMixin,generic.CreateView):
    model = Endpoint

@method_decorator(login_required, name="dispatch")
class EndpointUpdate(UpdatePopupMixin,UpdateMixin,generic.UpdateView):
    model = Endpoint

@method_decorator(login_required, name="dispatch")
class EndpointDelete(DeletePopupMixin,DeleteMixin,generic.DeleteView):
    model = Endpoint
           
@method_decorator(login_required,name='dispatch')
class NodeList(generics.ListCreateAPIView):
    """
        Create new OPCUA Configuration instances and visualize existing ones.
    """
    serializer_class = NodeSerializer
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Node.objects.all()
        else:
            return Node.objects.filter(endpoint__owner=user)

@method_decorator(login_required, name='dispatch')
class NodeDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Visualize and modify an existing OPCUA Node instance.
    """
    serializer_class = NodeSerializer
    permission_classes = [hasNodePermission]
    queryset = Node.objects.all()

@method_decorator(login_required, name="dispatch")
class NodeCreate(CreatePopupMixin,CreateMixin,generic.CreateView):
    model = Node

@method_decorator(login_required, name="dispatch")
class NodeUpdate(UpdatePopupMixin,UpdateMixin,generic.UpdateView):
    model = Node

@method_decorator(login_required, name="dispatch")
class NodeDelete(DeletePopupMixin,DeleteMixin,generic.DeleteView):
    model = Node
    
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

@method_decorator(login_required, name="dispatch")
class ProcessCreate(CreatePopupMixin,CreateMixin,generic.CreateView):
    model = Process

@method_decorator(login_required, name="dispatch")
class ProcessUpdate(UpdatePopupMixin,UpdateMixin,generic.UpdateView):
    model = Process

@method_decorator(login_required, name="dispatch")
class ProcessDelete(DeletePopupMixin,DeleteMixin,generic.DeleteView):
    model = Process

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

@method_decorator(login_required, name="dispatch")
class BatchCreate(CreatePopupMixin, CreateMixin, generic.CreateView):
    model = Batch

@method_decorator(login_required, name="dispatch")
class BatchUpdate(UpdatePopupMixin,UpdateMixin,generic.UpdateView):
    model = Batch

@method_decorator(login_required, name="dispatch")
class BatchDelete(DeletePopupMixin,DeleteMixin,generic.DeleteView):
    model = Batch

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

@method_decorator(login_required, name="dispatch")
class VariableCreate(CreatePopupMixin,CreateMixin,generic.CreateView):
    model = Variable

@method_decorator(login_required, name="dispatch")
class VariableUpdate(UpdatePopupMixin,UpdateMixin,generic.UpdateView):
    model = Variable

@method_decorator(login_required, name="dispatch")
class VariableDelete(DeletePopupMixin,DeleteMixin,generic.DeleteView):
    model = Variable

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

@method_decorator(login_required, name="dispatch")
class EventCreate(CreatePopupMixin,CreateMixin,generic.CreateView):
    model = Event
    
@method_decorator(login_required, name="dispatch")
class EventUpdate(UpdatePopupMixin,UpdateMixin,generic.UpdateView):
    model = Event

@method_decorator(login_required, name="dispatch")
class EventDelete(DeletePopupMixin,DeleteMixin,generic.DeleteView):
    model = Event
   

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


@method_decorator(login_required, name="dispatch")
class ClassCreate(CreatePopupMixin,CreateMixin,generic.CreateView):
    model = Class
  
@method_decorator(login_required, name="dispatch")
class ClassUpdate(UpdatePopupMixin,UpdateMixin,generic.UpdateView):
    model = Class 

@method_decorator(login_required, name="dispatch")
class ClassDelete(DeletePopupMixin,DeleteMixin,generic.DeleteView):
    model = Class

