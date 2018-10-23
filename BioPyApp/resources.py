from os import name

from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget, DateTimeWidget

from BioPyApp import models
from django.core.exceptions import ValidationError



class VariableResource(resources.ModelResource):    
    process = fields.Field(attribute="batch__process",column_name='process',widget=ForeignKeyWidget(models.Process,'name'))
    batch = fields.Field(attribute="batch",column_name='batch',widget=ForeignKeyWidget(models.Batch, 'name'))  

    class Meta:
        model = models.Variable
        fields = ('timestamp','batch','name','value')
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ('timestamp','batch','name','value')
        export_order = ('timestamp','process','batch','name','value')

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        user = kwargs['user']
        if not user.is_superuser:
            for row in dataset.dict:
                process=models.Process.objects.filter(name=row['process'],owner=user).first()
                if not process:
                    raise ValidationError('Could not find process \'%s\' for user \'%s\' defined in row %s.' % (process,user,row))
                else:
                    batch=models.Batch.objects.filter(name=row['batch'],process=process).first()
                    if not batch:
                        raise ValidationError('Could not find batch \'%s\' related to process \'%s\' for user \'%s\' for row %s' % (batch,process,user,row))
       
    def get_queryset(self):
        queryset = super(VariableResource, self).get_queryset()
        user = self.request.user
        if not user.is_superuser:
            queryset = self._meta.model.objects.filter(batch__process__owner=user)
        return queryset
        

 
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
