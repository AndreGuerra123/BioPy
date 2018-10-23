from BioPyApp.models import Process, Batch
from django.core.exceptions import ValidationError

def ProcessBatchDatasetValidator(dataset):
    for row in dataset.dict:
        user=
        rowid=
        process=Process.objects.get(name=row['process'],owner=user)
        if not process:
            raise ValidationError('Could not find process \'%s\' for user \'%s\' defined in row id \'%s\'.' % (process,user,rowid))
        batch=Batch.objects.get(name=row['batch'],process=process)
        if not batch:
            raise ValidationError('Could not find batch \'%s\' related to process \'%s\' for user \'%s\' for row id \'%s\'.' % (batch,process,user,rowid))

