from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from BioPyApp import models
from BioPyApp import resources

class VariableAdmin(ImportExportModelAdmin):
    def get_resource_class(self):
        return resources.VariableAdminResource

class EventAdmin(ImportExportModelAdmin):
    def get_resource_class(self):
        return resources.EventAdminResource

class ClassAdmin(ImportExportModelAdmin):
   def get_resource_class(self):
        return resources.ClassAdminResource

admin.site.register(models.Variable,VariableAdmin)
admin.site.register(models.Event,EventAdmin)
admin.site.register(models.Class, ClassAdmin)
admin.site.register(models.Endpoint)
admin.site.register(models.Node)
admin.site.register(models.Process)
admin.site.register(models.Batch)