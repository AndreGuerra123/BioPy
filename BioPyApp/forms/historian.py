from bootstrap_datepicker_plus import DateTimePickerInput
from django import forms
from django.forms.models import ModelMultipleChoiceField

from BioPyApp.models import Batch, Endpoint, Node, Process


class StepOneForm(forms.Form):
    process = forms.ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(StepOneForm, self).__init__(*args, **kwargs)
        self.fields['process'].queryset = Process.objects.filter(owner=user)

class StepTwoForm(forms.Form):
    batch = forms.ModelChoiceField(queryset=None)
    
    def __init__(self, *args, **kwargs):
        process = kwargs.pop('process')
        super(StepTwoForm, self).__init__(*args, **kwargs)
        self.fields['batch'].queryset = Batch.objects.filter(process=process)

class StepThreeForm(forms.Form):
    start = forms.DateTimeField(required=True, widget=DateTimePickerInput())
    end = forms.DateTimeField(required=True, widget=DateTimePickerInput())
    
    def __init__(self, *args, **kwargs):
        batch = kwargs.pop('batch')
        super(StepThreeForm, self).__init__(*args, **kwargs)
        self.fields['start'].initial = batch.start
        self.fields['end'].initial = batch.end


class StepFourForm(forms.Form):
    endpoints = ModelMultipleChoiceField(queryset=None)
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(StepFourForm, self).__init__(*args, **kwargs)
        self.fields['endpoints'].queryset = Endpoint.objects.filter(owner=user)

class StepFiveForm(forms.Form):
    nodes = ModelMultipleChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        endpoints = kwargs.pop('endpoints')
        super(StepFiveForm, self).__init__(*args, **kwargs)
        self.fields['nodes'].queryset = Node.objects.filter(endpoint__in=endpoints)

    


