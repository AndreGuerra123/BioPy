from bootstrap_datepicker_plus import DateTimePickerInput
from django import forms
from django.forms.models import ModelMultipleChoiceField

from BioPyApp.models import Batch, Endpoint, Node, Process


class StartEndForm(forms.Form):
    start = forms.DateTimeField(required=True, widget=DateTimePickerInput())
    end = forms.DateTimeField(required=True, widget=DateTimePickerInput())
    
    def __init__(self, *args, **kwargs):
        batch = kwargs.pop('batch')
        super(StartEndForm, self).__init__(*args, **kwargs)
        self.fields['start'].initial = batch.start
        self.fields['end'].initial = batch.end
    


