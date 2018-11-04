from django import forms
from django.forms.models import ModelMultipleChoiceField, ModelChoiceField
from django.urls import reverse_lazy

from BioPyApp.models import Endpoint, Node
from BioPyApp.widgets import CRUDWidgetWrapper


class SelectEndpointForm(forms.Form):
    endpoint = ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(SelectEndpointForm,self).__init__(*args, **kwargs)
        self.fields['endpoint'].queryset = Endpoint.objects.filter(owner=user)
        self.fields['endpoint'].widget = CRUDWidgetWrapper(
            self.fields['endpoint'].widget
            ,reverse_lazy('create_endpoint')
            ,reverse_lazy('update_endpoint',args=['__fk__'])
            ,reverse_lazy('delete_endpoint',args=['__fk__']))
      
    
class SelectNodeForm(forms.Form):
    node = ModelChoiceField(queryset=None)
    def __init__(self, *args, **kwargs):
        endpoints = kwargs.pop('endpoints')
        super(SelectNodeForm,self).__init__(*args, **kwargs)
        self.fields['node'].queryset = Node.objects.filter(endpoint__in=endpoints)
        self.fields['node'].widget = CRUDWidgetWrapper(
            self.fields['node'].widget
            ,reverse_lazy('create_node')
            ,reverse_lazy('update_node',args=['__fk__'])
            ,reverse_lazy('delete_node',args=['__fk__']))



class SelectMultipleEndpointsForm(forms.Form):
    endpoints = ModelMultipleChoiceField(queryset=None)
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(SelectMultipleEndpointsForm,self).__init__(*args, **kwargs)
        self.fields['endpoints'].queryset = Endpoint.objects.filter(owner=user)
        self.fields['endpoints'].widget = CRUDWidgetWrapper(
            self.fields['endpoints'].widget
            ,reverse_lazy('create_endpoint')
            ,reverse_lazy('update_endpoint',args=['__fk__'])
            ,reverse_lazy('delete_endpoint',args=['__fk__']))

class SelectMultipleNodesForm(forms.Form):
    nodes = ModelMultipleChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        endpoints = kwargs.pop('endpoints')
        super(SelectMultipleNodesForm,self).__init__(*args, **kwargs)
        self.fields['nodes'].queryset = Node.objects.filter(endpoint__in=endpoints)
        self.fields['nodes'].widget = CRUDWidgetWrapper(
            self.fields['nodes'].widget
            ,reverse_lazy('create_node')
            ,reverse_lazy('update_node',args=['__fk__'])
            ,reverse_lazy('delete_node',args=['__fk__']))
