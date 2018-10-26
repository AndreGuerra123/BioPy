from os import name

from .common import rgetattr
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from import_export import fields, resources
from import_export.widgets import CharWidget, ForeignKeyWidget

from BioPyApp.common import rgetattr
from BioPyApp.models import Batch, Class, Event, Process, Variable


class ProcessBatchForeignKeyWidget(ForeignKeyWidget):
    def get_queryset(self, value, row):
        return self.model.objects.filter(
            process__name=row["process"]
        )

class ProcessBatchResource(resources.ModelResource):
    process = fields.Field(column_name='process',widget=CharWidget())
    batch = fields.Field(attribute="batch",column_name='batch',widget=ProcessBatchForeignKeyWidget(Batch, 'name'))  

    def dehydrate_process(self,Instance):
        return rgetattr(Instance,'batch.process.name')
        
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        for row in dataset.dict:
            process_ins=Process.objects.filter(name=row['process'],owner=self.user).first()
            if not process_ins:
                raise ValidationError('Could not find process \'%s\' for user \'%s\' defined in row %s.' % (process_ins,self.user,row))
            batch_ins=Batch.objects.filter(name=row['batch'],process=process_ins).first()
            if not batch_ins:
                raise ValidationError('Could not find batch \'%s\' related to process \'%s\' for user \'%s\' for row %s' % (batch_ins,process_ins,self.user,row))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)


class VariableResource(ProcessBatchResource):    
    class Meta:        
        model = Variable
        skip_unchanged = True
        report_skipped = True
        exclude = ('id','created','modified')
        import_id_fields = ('batch','name','timestamp') 
        export_order = ('timestamp','process','batch','name','value')

    def get_queryset(self):
        if not self.user.is_superuser:
            return Variable.objects.filter(batch__process__owner=self.user)
        else:
            return Variable.objects.all()


class EventResource(ProcessBatchResource):

    class Meta:
        model = Event
        skip_unchanged = True
        report_skipped = True
        exclude = ('id','created','modified')
        import_id_fields = ('batch','name','timestamp') 
        export_order = ('timestamp','process','batch','name')

    def get_queryset(self):
        if not self.user.is_superuser:
            return Event.objects.filter(batch__process__owner=self.user)
        else:
            return Event.objects.all()
     

class ClassResource(ProcessBatchResource):

    class Meta:
        model = Class
        skip_unchanged = True
        report_skipped = True
        exclude = ('id','created','modified')
        import_id_fields = ('batch','name','value')
        export_order = ('process','batch','name','value')

    def get_queryset(self):
        if not self.user.is_superuser:
            return Class.objects.filter(batch__process__owner=self.user)
        else:
            return Class.objects.all()


class ProcessBatchAdminForeignKeyWidget(ForeignKeyWidget):
    def get_queryset(self, value, row):
        return self.model.objects.filter(
            process__owner__username=row["user"],
            process__name=row["process"]
        )

class ProcessBatchAdminResource(resources.ModelResource):
    user = fields.Field(column_name='user',widget=CharWidget())
    process = fields.Field(column_name='process',widget=CharWidget())
    batch = fields.Field(attribute="batch",column_name='batch',widget=ProcessBatchAdminForeignKeyWidget(Batch, 'name'))  

    def dehydrate_process(self,Instance):
        return rgetattr(Instance,'batch.process.name')
        
    def dehydrate_user(self,Instance):
        return rgetattr(Instance,'batch.process.owner.username')

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        for row in dataset.dict:
            user_ins=get_user_model().objects.filter(username=row["user"]).first()
            if not user_ins:
                raise ValidationError('Could not find for user \'%s\' defined in row %s.' % (user_ins,row))
            process_ins=Process.objects.filter(name=row['process'],owner=user_ins).first()
            if not process_ins:
                raise ValidationError('Could not find process \'%s\' for user \'%s\' defined in row %s.' % (process_ins,user_ins,row))
            batch_ins=Batch.objects.filter(name=row['batch'],process=process_ins).first()
            if not batch_ins:
                raise ValidationError('Could not find batch \'%s\' related to process \'%s\' for user \'%s\' for row %s' % (batch_ins,process_ins,user_ins,row))


class VariableAdminResource(ProcessBatchAdminResource):
    
    class Meta:        
        model = Variable
        skip_unchanged = True
        report_skipped = True
        exclude = ('id','created','modified')
        import_id_fields = ('batch','name','timestamp') 
        export_order = ('timestamp','user','process','batch','name','value')

class EventAdminResource(ProcessBatchAdminResource):    
    
    class Meta:
        model = Event
        skip_unchanged = True
        report_skipped = True
        exclude = ('id','created','modified')
        import_id_fields = ('batch','name','timestamp') 
        export_order = ('timestamp','user','process','batch','name')

    
class ClassAdminResource(ProcessBatchAdminResource):    
     
    class Meta:
        model = Class
        skip_unchanged = True
        report_skipped = True
        exclude = ('id','created','modified')
        import_id_fields = ('batch','name','value')
        export_order = ('user','process','batch','name','value')

    