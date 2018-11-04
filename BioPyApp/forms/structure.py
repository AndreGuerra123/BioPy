from django import forms
from django.urls import reverse_lazy
from BioPyApp.models import Process, Batch, Variable, Class, Event
from BioPyApp.widgets import CRUDWidgetWrapper

class SelectProcessForm(forms.Form):
    process = forms.models.ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(SelectProcessForm,self).__init__(*args, **kwargs)
        self.fields['process'].queryset = Process.objects.filter(owner=user)
        self.fields['process'].widget = CRUDWidgetWrapper(
            self.fields['process'].widget
            ,reverse_lazy('create_process')
            ,reverse_lazy('update_process',args=['__fk__'])
            ,reverse_lazy('delete_process',args=['__fk__']))
      
    
class SelectBatchForm(forms.Form):
    batch = forms.models.ModelChoiceField(queryset=None)
    
    def __init__(self, *args, **kwargs):
        process = kwargs.pop('process')
        super(SelectBatchForm,self).__init__(*args, **kwargs)
        self.fields['batch'].queryset = Batch.objects.filter(process=process)
        self.fields['batch'].widget = CRUDWidgetWrapper(
            self.fields['batch'].widget
            ,reverse_lazy('create_batch')
            ,reverse_lazy('update_batch',args=['__fk__'])
            ,reverse_lazy('delete_batch',args=['__fk__']))

class DataConfigurationForm(forms.Form):

    variables = forms.models.ModelChoiceField(queryset=None)
    classes = forms.models.ModelChoiceField(queryset=None)
    events = forms.models.ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        batch = kwargs.pop('batch')
        super(DataConfigurationForm,self).__init__(*args, **kwargs)
    
        self.fields['variables'].queryset = Variable.objects.filter(batch=batch)
        self.fields['variables'].widget = CRUDWidgetWrapper(
            self.fields['variables'].widget
            ,reverse_lazy('create_variable')
            ,reverse_lazy('update_variable',args=['__fk__'])
            ,reverse_lazy('delete_variable',args=['__fk__']))

        self.fields['events'].queryset = Event.objects.filter(batch=batch)
        self.fields['events'].widget = CRUDWidgetWrapper(
            self.fields['events'].widget
            ,reverse_lazy('create_event')
            ,reverse_lazy('update_event',args=['__fk__'])
            ,reverse_lazy('delete_event',args=['__fk__']))

        self.fields['classes'].queryset = Class.objects.filter(batch=batch)
        self.fields['classes'].widget = CRUDWidgetWrapper(
            self.fields['classes'].widget
            ,reverse_lazy('create_class')
            ,reverse_lazy('update_class',args=['__fk__'])
            ,reverse_lazy('delete_class',args=['__fk__']))