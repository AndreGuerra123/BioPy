from django import forms
from django.urls import reverse_lazy
from rest_framework.fields import ChoiceField

from BioPyApp.models import Batch, Class, Event, Process, Variable
from BioPyApp.widgets import CRUDWidgetWrapper

unfolding_method_options = (
    ("idx","Indexed"),
    ("ts","Timeseries"),
    ("bw_tv","Batch-wise (TxV)"),
    ("bw_vt","Batch-wise (VxT)"),
    ("vw_bt","Variable-wise (BxT)"),
    ("vw_tb","Variable-wise (TxB)"),
    ("tw_bv","Time-wise (BxV)"),
    ("tw_vb","Time-wise (VxB)"),
)
unfolding_axis_options = (("x","X Axis (Column)"),("y","Y Axis (Row)"))
time_reference_options = [("elapsed","Elapsed"),("timestamp","Absolute")]
compression_options = (('sparse',"Sparse"),('dense','Dense'))
file_format_options=["parquet","pickle","csv","hdf","xlsx","json","feather","stata","msgpack"]


class SelectVariablePredictorsForm(forms.Form):

    predictors = forms.MultipleChoiceField()
    
    def __init__(self, *args, **kwargs):
        batches = kwargs.pop('batches')
        super(SelectVariablePredictorsForm,self).__init__(*args, **kwargs)
        preds=Variable.objects.filter(batch__in=batches).values_list('name',flat=True).distinct()
        choices = [(p,p) for p in preds ]
        self.fields['predictors'].choices = choices
        self.fields['predictors'].widget = CRUDWidgetWrapper(
            self.fields['predictors'].widget
            ,reverse_lazy('create_variable'),None,None)

class SelectEventPredictorsForm(forms.Form):

    predictors = forms.MultipleChoiceField()
    
    def __init__(self, *args, **kwargs):
        batches = kwargs.pop('batches')
        super(SelectEventPredictorsForm,self).__init__(*args, **kwargs)
        preds=Event.objects.filter(batch__in=batches).values_list('name',flat=True).distinct()
        choices = [(p,p) for p in preds]
        self.fields['predictors'].choices = choices
        self.fields['predictors'].widget = CRUDWidgetWrapper(
            self.fields['predictors'].widget
            ,reverse_lazy('create_event'),None,None)

class SelectClassPredictorsForm(forms.Form):

    predictors = forms.MultipleChoiceField()
    
    def __init__(self, *args, **kwargs):
        batches = kwargs.pop('batches')
        super(SelectClassPredictorsForm,self).__init__(*args, **kwargs)
        preds=Class.objects.filter(batch__in=batches).values_list('name',flat=True).distinct()
        choices = [(p,p) for p in preds]
        self.fields['predictors'].choices = choices
        self.fields['predictors'].widget = CRUDWidgetWrapper(
            self.fields['predictors'].widget
            ,reverse_lazy('create_class'),None,None)

class SelectSingleProcessDataframeOptionsForm(forms.Form):
    unfolding_method = forms.ChoiceField(choices=unfolding_method_options)
    unfolding_axis = forms.ChoiceField(choices=unfolding_axis_options)
    time_reference = forms.ChoiceField(choices=time_reference_options)
    compression = forms.ChoiceField(choices=compression_options)
    file_format = forms.ChoiceField(choices=zip(file_format_options,[o.title() for o in file_format_options]))

class MultiProcessForm(forms.Form):
    pass
