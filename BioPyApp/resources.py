from os import name

from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from BioPyApp import models


class VariableResource(resources.ModelResource):
    process = fields.Field(attribute='process',column_name='process',widget=ForeignKeyWidget(models.Process,'name'))
    batch = fields.Field(attribute='batch',column_name='batch',widget=ForeignKeyWidget(models.Batch, 'name'))   

    class Meta:
        model = models.Variable
        exclude = ('created','modified')
        export_order = ('id', 'timestamp','process', 'batch', 'name','value')
 
class EventResource(resources.ModelResource):
    timestamp = fields.Field(attribute='timestamp',column_name='timestamp')
    batch = fields.Field(attribute='batch',column_name='batch',widget=ForeignKeyWidget(models.Batch, 'name'))   
    name = fields.Field(attribute='name',column_name='name')
    value = fields.Field(attribute='value',column_name='value')

    class Meta:
        fields = ('timestamp','batch','name','value')


class ClassResource(resources.ModelResource):
    batch = fields.Field(attribute='batch',column_name='batch',widget=ForeignKeyWidget(models.Batch, 'name'))   
    name = fields.Field(attribute='name',column_name='name')
    value = fields.Field(attribute='value',column_name='value')

    class Meta:
        fields = ('batch','name','value')
