import os
import tempfile
from builtins import getattr
from datetime import datetime

from BioPyApp.forms import historian
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.translation import gettext as _
from django.views import generic
from formtools.wizard.views import SessionWizardView
from import_export.formats.base_formats import DEFAULT_FORMATS
from import_export.forms import ConfirmImportForm, ExportForm, ImportForm
from import_export.resources import RowResult, modelresource_factory
from import_export.tmp_storages import TempFolderStorage
from rest_framework import generics

from BioPyApp.models import Batch, Class, Endpoint, Event, Node, Process, \
    Variable
from BioPyApp.opcua import HistorianImporter
from BioPyApp.permissions import hasBatchPermission, hasDataPermission, \
    hasEndpointPermission, hasNodePermission, hasProcessPermission
from BioPyApp.resources import ClassResource, EventResource, VariableResource
from BioPyApp.serializers import BatchSerializer, ClassSerializer, \
    EndpointSerializer, EventSerializer, NodeSerializer, ProcessSerializer, \
    VariableSerializer


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

# Actions
@method_decorator(login_required,name='dispatch')
class ActionsView(generic.TemplateView):
    template_name = 'actions/actions.html'

## Input Data
@method_decorator(login_required,name='dispatch')
class InputView(generic.TemplateView):
    template_name = 'actions/input/input.html'

### Realtime

### Historian 
@method_decorator(login_required,name="dispatch")
class HistorianWizardView(SessionWizardView):
    form_list = [
        ("step_one", historian.StepOneForm),
        ("step_two", historian.StepTwoForm),
        ("step_three", historian.StepThreeForm),
        ("step_four", historian.StepFourForm),
        ("step_five", historian.StepFiveForm),
        ]

    template_name = "actions/input/historian/historian.html"

    def get_form_kwargs(self, step):
        if step == 'step_one': #selects process
            return {'user': self.request.user}
        elif step == 'step_two' : # selects batch
            return {'process':self.get_cleaned_data_for_step('step_one').get('process')}
        elif step == 'step_three': # selects limits
            return {'batch':self.get_cleaned_data_for_step('step_two').get('batch')}
        elif step == 'step_four': # selects endpoints
            return {'user':self.request.user}
        elif step == 'step_five': # selectes nodes
            return {'endpoints':self.get_cleaned_data_for_step('step_four').get('endpoints')}
        else:
            return {}
    
    def done(self,form_list,**kwargs):
        context={}
        template = 'actions/input/historian/historian_importer.html'
        params=[form.cleaned_data for form in form_list]
        results=HistorianImporter(params)
        context['results'] = results
        return TemplateResponse(self.request, [template], context)


@login_required
def historian_processor(request,datasets):
    
    variables_dataset = datasets.getattr('variables',None)
    classes_dataset = datasets.getattr('classes',None)
    events_dataset = datasets.getattr('events',None)

    if variables_dataset:
        VariableResource(request.user).import_data(dataset=variables_dataset,dry_run=False,raise_errors=True,user=request.user)
    if classes_dataset:
        ClassResource(request.user).import_data(dataset=classes_dataset,dry_run=False,raise_errors=True,user=request.user)
    if events_dataset:
        EventResource(request.user).import_data(dataset=events_dataset,dry_run=False,raise_errors=True,user=request.user)

    return HttpResponseRedirect(reverse('home'))
    
### Import Files
@method_decorator(login_required,name='dispatch')
class ImportView(generic.TemplateView):
    template_name = 'actions/input/import/import.html'

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

#### VariableFileImport
@method_decorator(login_required, name="dispatch") 
class VariableFileImport(generic.View):
    def get(self,*args, **kwargs):
        return importer(
            self.request,
            VariableResource(self.request.user),
            'actions/input/import/variable_file_import.html')

    def post(self,*args,**kwargs):
        return importer(
            self.request,
            VariableResource(self.request.user),
            'actions/input/import/variable_file_import.html')

#### VariableFileProcessingImport
@method_decorator(login_required,name='dispatch')
class VariableFileImportProcessing(generic.View):
    def post(self,*args,**kwargs):
        return processor(
            self.request,
            VariableResource(self.request.user),
            'actions/input/import/variable_file_import.html',
            'variables_list')    
        
#### EventFileImport   
@method_decorator(login_required,name='dispatch')
class EventFileImport(generic.TemplateView):
    def get(self,*args, **kwargs):
        return importer(
            self.request,
            EventResource(self.request.user),
            'actions/input/import/event_file_import.html')

    def post(self,*args,**kwargs):
        return importer(
            self.request,
            EventResource(self.request.user),
            'actions/input/import/event_file_import.html')

#### EventFileProcessingImport
@method_decorator(login_required,name='dispatch')
class EventFileImportProcessing(generic.View):
    def post(self,*args,**kwargs):
        return processor(
            self.request,
            EventResource(self.request.user),
            'actions/input/import/event_file_import.html',
            'events_list')

#### ClassFileImport   
@method_decorator(login_required,name='dispatch')
class ClassFileImport(generic.View):
    def get(self,*args, **kwargs):
        return importer(
            self.request,
            ClassResource(self.request.user),
            'actions/input/import/class_file_import.html')

    def post(self,*args,**kwargs):
        return importer(
            self.request,
            ClassResource(self.request.user),
            'actions/input/import/class_file_import.html')

#### ClassFileProcessingImport
@method_decorator(login_required,name='dispatch')
class ClassFileImportProcessing(generic.View):
    def post(self,*args,**kwargs):
        return processor(
            self.request,
            ClassResource(self.request.user),
            'actions/input/import/class_file_import.html',
            'classes_list')  


## Output Data
@method_decorator(login_required,name='dispatch')
class OutputView(generic.TemplateView):
    template_name = 'actions/output/output.html'

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
            'actions/output/export/variable_file_export.html')

    def post(self,*args,**kwargs):
        return exporter(
            self.request,
            VariableResource(self.request.user),
            'actions/output/export/variable_file_export.html')

@method_decorator(login_required, name="dispatch") 
class ClassFileExport(generic.View):
    def get(self,*args, **kwargs):
        return exporter(self.request,
            ClassResource(self.request.user),
            'actions/output/export/class_file_export.html')

    def post(self,*args,**kwargs):
        return exporter(
            self.request,
            ClassResource(self.request.user),
            'actions/output/export/class_file_export.html')

@method_decorator(login_required, name="dispatch") 
class EventFileExport(generic.View):
    def get(self,*args, **kwargs):
        return exporter(self.request,
            EventResource(self.request.user),
            'actions/output/export/event_file_export.html')

    def post(self,*args,**kwargs):
        return exporter(
            self.request,
            EventResource(self.request.user),
            'actions/output/export/event_file_export.html')

### Dataset
@method_decorator(login_required,name='dispatch')
class DatasetView(generic.TemplateView):
    template_name = 'actions/output/dataset/dataset.html'
#TODO: All types

### Export Files
@method_decorator(login_required,name='dispatch')
class ExportView(generic.TemplateView):
    template_name = 'actions/output/export/export.html'
#TODO: ALL types

## View Data
@method_decorator(login_required,name='dispatch')
class ViewView(generic.TemplateView):
    template_name = 'actions/view/view.html'

# API views
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
    

