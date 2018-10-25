import os
import tempfile

from .models import Batch, Class, Endpoint, Event, Node, Process, Variable
from .permissions import hasBatchPermission, hasDataPermission, \
    hasEndpointPermission, hasNodePermission, hasProcessPermission
from .resources import ClassResource, EventResource, VariableResource
from .serializers import BatchSerializer, ClassSerializer, EndpointSerializer, \
    EventSerializer, NodeSerializer, ProcessSerializer, VariableSerializer
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.translation import gettext as _
from django.views import generic
from import_export.formats import base_formats
from import_export.forms import ConfirmImportForm, ImportForm
from import_export.resources import RowResult, modelresource_factory
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

# Actions
@method_decorator(login_required,name='dispatch')
class ActionsView(generic.TemplateView):
    template_name = 'actions/actions.html'

## Data Acquisition
@method_decorator(login_required,name='dispatch')
class AcquisitionView(generic.TemplateView):
    template_name = 'actions/acquisition/acquisition.html'

### Online

### Offline

### Import
@method_decorator(login_required,name='dispatch')
class ImportView(generic.TemplateView):
    template_name = 'actions/acquisition/import/import.html'

#### VariableFileImport   
@method_decorator(login_required,name='dispatch')
class VariableFileImport(generic.View):
    from_encoding = "utf-8"
    formats = (
        base_formats.CSV,
        base_formats.XLS,
        base_formats.TSV,
        base_formats.ODS,
        base_formats.JSON,
        base_formats.YAML,
        base_formats.HTML,
    )
    template_name = 'actions/acquisition/import/variable_file_import.html'

    def get_import_formats(self):
        """
        Returns available import formats.
        """
        return [f for f in self.formats if f().can_import()]

    def get(self, *args, **kwargs ):
        '''
        Perform a dry_run of the import to make sure the import will not
        result in errors.  If there where no error, save the user
        uploaded file to a local temp file that will be used by
        'process_import' for the actual import.
        '''
        resource = VariableResource(self.request.user)
        context = {}
        import_formats = self.get_import_formats()
        form = ImportForm(import_formats,
                          self.request.POST or None,
                          self.request.FILES or None)

        if self.request.POST and form.is_valid():
            input_format = import_formats[
                int(form.cleaned_data['input_format'])
            ]()
            import_file = form.cleaned_data['import_file']
            # first always write the uploaded file to disk as it may be a
            # memory file or else based on settings upload handlers
            with tempfile.NamedTemporaryFile(delete=False) as uploaded_file:
                for chunk in import_file.chunks():
                    uploaded_file.write(chunk)

            # then read the file, using the proper format-specific mode
            with open(uploaded_file.name,
                      input_format.get_read_mode()) as uploaded_import_file:
                # warning, big files may exceed memory
                data = uploaded_import_file.read()
                if not input_format.is_binary() and self.from_encoding:
                    data = force_text(data, self.from_encoding)
                dataset = input_format.create_dataset(data)
                result = resource.import_data(dataset, dry_run=True,
                                              raise_errors=False)

            context['result'] = result

            if not result.has_errors():
                context['confirm_form'] = ConfirmImportForm(initial={
                    'import_file_name': os.path.basename(uploaded_file.name),
                    'input_format': form.cleaned_data['input_format'],
                })

        context['form'] = form
        context['fields'] = [f.column_name for f in resource.get_fields()]

        return TemplateResponse(self.request, [self.template_name], context)

    def post(self, *args, **kwargs ):
        '''
        Perform a dry_run of the import to make sure the import will not
        result in errors.  If there where no error, save the user
        uploaded file to a local temp file that will be used by
        'process_import' for the actual import.
        '''
        resource = VariableResource(self.request.user)
        context = {}
        import_formats = self.get_import_formats()
        form = ImportForm(import_formats,
                          self.request.POST or None,
                          self.request.FILES or None)

        if self.request.POST and form.is_valid():
            input_format = import_formats[
                int(form.cleaned_data['input_format'])
            ]()
            import_file = form.cleaned_data['import_file']
            # first always write the uploaded file to disk as it may be a
            # memory file or else based on settings upload handlers
            with tempfile.NamedTemporaryFile(delete=False) as uploaded_file:
                for chunk in import_file.chunks():
                    uploaded_file.write(chunk)

            # then read the file, using the proper format-specific mode
            with open(uploaded_file.name,
                      input_format.get_read_mode()) as uploaded_import_file:
                # warning, big files may exceed memory
                data = uploaded_import_file.read()
                if not input_format.is_binary() and self.from_encoding:
                    data = force_text(data, self.from_encoding)
                dataset = input_format.create_dataset(data)
                result = resource.import_data(dataset, dry_run=True,
                                              raise_errors=False)

            context['result'] = result

            if not result.has_errors():
                context['confirm_form'] = ConfirmImportForm(initial={
                    'import_file_name': os.path.basename(uploaded_file.name),
                    'input_format': form.cleaned_data['input_format'],
                })

        context['form'] = form
        context['fields'] = [f.column_name for f in resource.get_fields()]

        return TemplateResponse(self.request, [self.template_name], context)

#### VariableFileProcessingImport
@method_decorator(login_required,name='dispatch')
class VariableFileImportProcessing(generic.View):
    from_encoding = "utf-8"
    formats = (
        base_formats.CSV,
        base_formats.XLS,
        base_formats.TSV,
        base_formats.ODS,
        base_formats.JSON,
        base_formats.YAML,
        base_formats.HTML,
    )
    template_name = 'actions/acquisition/import/variable_file_import.html'

    def get_import_formats(self):
        """
        Returns available import formats.
        """
        return [f for f in self.formats if f().can_import()]

    def post(self, *args, **kwargs ):
        '''
        Perform the actual import action (after the user has confirmed he
        wishes to import)
        '''
        resource = VariableResource(self.request.user)
        confirm_form = ConfirmImportForm(self.request.POST)
        if confirm_form.is_valid():
            import_formats = self.get_import_formats()
            input_format = import_formats[
                int(confirm_form.cleaned_data['input_format'])
            ]()
            import_file_name = os.path.join(
                tempfile.gettempdir(),
                confirm_form.cleaned_data['import_file_name']
            )
            import_file = open(import_file_name, input_format.get_read_mode())
            data = import_file.read()
            if not input_format.is_binary() and self.from_encoding:
                data = force_text(data, self.from_encoding)
            dataset = input_format.create_dataset(data)

            resource.import_data(dataset, dry_run=False, raise_errors=True)

            success_message = _('Import sucessfull')
            messages.success(self.request, success_message)
            import_file.close()           
            return HttpResponseRedirect(reverse_lazy('variables_list'))

#### EventFileImport   
@method_decorator(login_required,name='dispatch')
class EventFileImport(generic.TemplateView):
    from_encoding = "utf-8"
    formats = (
        base_formats.CSV,
        base_formats.XLS,
        base_formats.TSV,
        base_formats.ODS,
        base_formats.JSON,
        base_formats.YAML,
        base_formats.HTML,
    )
    template_name = 'actions/acquisition/import/event_file_import.html'

    def get_import_formats(self):
        """
        Returns available import formats.
        """
        return [f for f in self.formats if f().can_import()]

    def get(self, *args, **kwargs ):
        '''
        Perform a dry_run of the import to make sure the import will not
        result in errors.  If there where no error, save the user
        uploaded file to a local temp file that will be used by
        'process_import' for the actual import.
        '''
        resource = EventResource(self.request.user)
        context = self.get_context_data()
        import_formats = self.get_import_formats()
        form = ImportForm(import_formats,
                          self.request.POST or None,
                          self.request.FILES or None)

        if self.request.POST and form.is_valid():
            input_format = import_formats[
                int(form.cleaned_data['input_format'])
            ]()
            import_file = form.cleaned_data['import_file']
            # first always write the uploaded file to disk as it may be a
            # memory file or else based on settings upload handlers
            with tempfile.NamedTemporaryFile(delete=False) as uploaded_file:
                for chunk in import_file.chunks():
                    uploaded_file.write(chunk)

            # then read the file, using the proper format-specific mode
            with open(uploaded_file.name,
                      input_format.get_read_mode()) as uploaded_import_file:
                # warning, big files may exceed memory
                data = uploaded_import_file.read()
                if not input_format.is_binary() and self.from_encoding:
                    data = force_text(data, self.from_encoding)
                dataset = input_format.create_dataset(data)
                result = resource.import_data(dataset, dry_run=True,
                                              raise_errors=False)

            context['result'] = result

            if not result.has_errors():
                context['confirm_form'] = ConfirmImportForm(initial={
                    'import_file_name': os.path.basename(uploaded_file.name),
                    'input_format': form.cleaned_data['input_format'],
                })

        context['form'] = form
        context['fields'] = [f.column_name for f in resource.get_fields()]

        return TemplateResponse(self.request, [self.template_name], context)

    def post(self, *args, **kwargs ):
        '''
        Perform a dry_run of the import to make sure the import will not
        result in errors.  If there where no error, save the user
        uploaded file to a local temp file that will be used by
        'process_import' for the actual import.
        '''
        resource = EventResource(self.request.user)
        context = self.get_context_data()
        import_formats = self.get_import_formats()
        form = ImportForm(import_formats,
                          self.request.POST or None,
                          self.request.FILES or None)

        if self.request.POST and form.is_valid():
            input_format = import_formats[
                int(form.cleaned_data['input_format'])
            ]()
            import_file = form.cleaned_data['import_file']
            # first always write the uploaded file to disk as it may be a
            # memory file or else based on settings upload handlers
            with tempfile.NamedTemporaryFile(delete=False) as uploaded_file:
                for chunk in import_file.chunks():
                    uploaded_file.write(chunk)

            # then read the file, using the proper format-specific mode
            with open(uploaded_file.name,
                      input_format.get_read_mode()) as uploaded_import_file:
                # warning, big files may exceed memory
                data = uploaded_import_file.read()
                if not input_format.is_binary() and self.from_encoding:
                    data = force_text(data, self.from_encoding)
                dataset = input_format.create_dataset(data)
                result = resource.import_data(dataset, dry_run=True,
                                              raise_errors=False)

            context['result'] = result

            if not result.has_errors():
                context['confirm_form'] = ConfirmImportForm(initial={
                    'import_file_name': os.path.basename(uploaded_file.name),
                    'input_format': form.cleaned_data['input_format'],
                })

        context['form'] = form
        context['fields'] = [f.column_name for f in resource.get_fields()]

        return TemplateResponse(self.request, [self.template_name], context)

#### EventFileProcessingImport
@method_decorator(login_required,name='dispatch')
class EventFileImportProcessing(generic.View):
    from_encoding = "utf-8"
    formats = (
        base_formats.CSV,
        base_formats.XLS,
        base_formats.TSV,
        base_formats.ODS,
        base_formats.JSON,
        base_formats.YAML,
        base_formats.HTML,
    )
    import_template_name = 'actions/acquisition/import/event_file_import.html'

    def get_import_formats(self):
        """
        Returns available import formats.
        """
        return [f for f in self.formats if f().can_import()]

    def post(self, *args, **kwargs ):
        '''
        Perform the actual import action (after the user has confirmed he
    wishes to import)
        '''
        resource = EventResource(self.request.user)
        confirm_form = ConfirmImportForm(self.request.POST)
        if confirm_form.is_valid():
            import_formats = self.get_import_formats()
            input_format = import_formats[
                int(confirm_form.cleaned_data['input_format'])
            ]()
            import_file_name = os.path.join(
                tempfile.gettempdir(),
                confirm_form.cleaned_data['import_file_name']
            )
            import_file = open(import_file_name, input_format.get_read_mode())
            data = import_file.read()
            if not input_format.is_binary() and self.from_encoding:
                data = force_text(data, self.from_encoding)
            dataset = input_format.create_dataset(data)

            resource.import_data(dataset, dry_run=False, raise_errors=True)

            success_message = _('Import sucessfull')
            messages.success(self.request, success_message)
            import_file.close()
            return HttpResponseRedirect(reverse('events_list'))

#### ClassFileImport   
@method_decorator(login_required,name='dispatch')
class ClassFileImport(generic.View):
    from_encoding = "utf-8"
    formats = (
        base_formats.CSV,
        base_formats.XLS,
        base_formats.TSV,
        base_formats.ODS,
        base_formats.JSON,
        base_formats.YAML,
        base_formats.HTML,
    )
    template_name = 'actions/acquisition/import/class_file_import.html'

    def get_import_formats(self):
        """
        Returns available import formats.
        """
        return [f for f in self.formats if f().can_import()]

    def get(self, *args, **kwargs ):
        '''
        Perform a dry_run of the import to make sure the import will not
        result in errors.  If there where no error, save the user
        uploaded file to a local temp file that will be used by
        'process_import' for the actual import.
        '''
        resource = ClassResource(self.request.user)
        context = {}

        import_formats = self.get_import_formats()
        form = ImportForm(import_formats,
                          self.request.POST or None,
                          self.request.FILES or None)

        if self.request.POST and form.is_valid():
            input_format = import_formats[
                int(form.cleaned_data['input_format'])
            ]()
            import_file = form.cleaned_data['import_file']
            # first always write the uploaded file to disk as it may be a
            # memory file or else based on settings upload handlers
            with tempfile.NamedTemporaryFile(delete=False) as uploaded_file:
                for chunk in import_file.chunks():
                    uploaded_file.write(chunk)

            # then read the file, using the proper format-specific mode
            with open(uploaded_file.name,
                      input_format.get_read_mode()) as uploaded_import_file:
                # warning, big files may exceed memory
                data = uploaded_import_file.read()
                if not input_format.is_binary() and self.from_encoding:
                    data = force_text(data, self.from_encoding)
                dataset = input_format.create_dataset(data)
                result = resource.import_data(dataset, dry_run=True,
                                              raise_errors=False)

            context['result'] = result

            if not result.has_errors():
                context['confirm_form'] = ConfirmImportForm(initial={
                    'import_file_name': os.path.basename(uploaded_file.name),
                    'input_format': form.cleaned_data['input_format'],
                })

        context['form'] = form
        context['fields'] = [f.column_name for f in resource.get_fields()]

        return TemplateResponse(self.request, [self.template_name], context)

    def post(self, *args, **kwargs ):
        '''
        Perform a dry_run of the import to make sure the import will not
        result in errors.  If there where no error, save the user
        uploaded file to a local temp file that will be used by
        'process_import' for the actual import.
        '''
        resource = ClassResource(self.request.user)
        context = {}
        import_formats = self.get_import_formats()
        form = ImportForm(import_formats,
                          self.request.POST or None,
                          self.request.FILES or None)

        if self.request.POST and form.is_valid():
            input_format = import_formats[
                int(form.cleaned_data['input_format'])
            ]()
            import_file = form.cleaned_data['import_file']
            # first always write the uploaded file to disk as it may be a
            # memory file or else based on settings upload handlers
            with tempfile.NamedTemporaryFile(delete=False) as uploaded_file:
                for chunk in import_file.chunks():
                    uploaded_file.write(chunk)

            # then read the file, using the proper format-specific mode
            with open(uploaded_file.name,
                      input_format.get_read_mode()) as uploaded_import_file:
                # warning, big files may exceed memory
                data = uploaded_import_file.read()
                if not input_format.is_binary() and self.from_encoding:
                    data = force_text(data, self.from_encoding)
                dataset = input_format.create_dataset(data)
                result = resource.import_data(dataset, dry_run=True,
                                              raise_errors=False)

            context['result'] = result

            if not result.has_errors():
                context['confirm_form'] = ConfirmImportForm(initial={
                    'import_file_name': os.path.basename(uploaded_file.name),
                    'input_format': form.cleaned_data['input_format'],
                })

        context['form'] = form
        context['fields'] = [f.column_name for f in resource.get_fields()]

        return TemplateResponse(self.request, [self.template_name], context)

#### ClassFileProcessingImport
@method_decorator(login_required,name='dispatch')
class ClassFileImportProcessing(generic.View):
    from_encoding = "utf-8"
    formats = (
        base_formats.CSV,
        base_formats.XLS,
        base_formats.TSV,
        base_formats.ODS,
        base_formats.JSON,
        base_formats.YAML,
        base_formats.HTML,
    )
    template_name = 'actions/acquisition/import/class_file_import.html'

    def get_import_formats(self):
        """
        Returns available import formats.
        """
        return [f for f in self.formats if f().can_import()]

    def post(self, *args, **kwargs ):
        '''
        Perform the actual import action (after the user has confirmed he
        wishes to import)
        '''
        resource = ClassResource(self.request.user)
        confirm_form = ConfirmImportForm(self.request.POST)
        if confirm_form.is_valid():
            import_formats = self.get_import_formats()
            input_format = import_formats[
                int(confirm_form.cleaned_data['input_format'])
            ]()
            import_file_name = os.path.join(
                tempfile.gettempdir(),
                confirm_form.cleaned_data['import_file_name']
            )
            import_file = open(import_file_name, input_format.get_read_mode())
            data = import_file.read()
            if not input_format.is_binary() and self.from_encoding:
                data = force_text(data, self.from_encoding)
            dataset = input_format.create_dataset(data)

            resource.import_data(dataset, dry_run=False, raise_errors=True)

            success_message = _('Import sucessfull')
            messages.success(self.request, success_message)
            import_file.close()
            return HttpResponseRedirect(reverse('classes_list'))

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
    

