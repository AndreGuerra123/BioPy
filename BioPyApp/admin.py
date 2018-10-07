from django.contrib import admin
from BioPyApp import models

admin.site.register(models.Process)
admin.site.register(models.Batch)
admin.site.register(models.Variable)
admin.site.register(models.Event)
admin.site.register(models.Class)
