import datetime
import io
from tempfile import NamedTemporaryFile

import pandas as pd
from django.http import HttpResponseRedirect
from django.urls import reverse
from django_downloadview import VirtualDownloadView
from formtools.wizard.views import SessionWizardView

from BioPyApp.forms import structure, dataframe
from BioPyApp.drivers.dataframe import get_model_dataframe
from BioPyApp.drivers.opcua import OPCUAHistorianImporter

class DataframeDownload(VirtualDownloadView):

    def get_parameters(self):
        return self.request.session['params']

    def get_description(self):
        unf = self.get_parameters()['unfolding_method']
        return '_'.join([self.model.__name__,unf])

    def get_prefix(self):
        return '_'.join([self.get_description(),datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),"_"])
  
    def get_suffix(self):
        return "".join([".",self.get_parameters()['file_format']])

    def get_file(self):
        tf = NamedTemporaryFile(suffix=self.get_suffix(),prefix=self.get_prefix())
        params = self.get_parameters()
        ff= params['file_format']
        if(ff=="parquet"):
            self.get_dataframe().to_parquet(tf.name,use_deprecated_int96_timestamps=True)
        elif(ff=="pickle"):
            self.get_dataframe().to_pickle(tf.name)
        elif(ff=="csv"):
            self.get_dataframe().to_csv(tf.name)
        elif(ff=="hdf"):
            self.get_dataframe().to_hdf(tf.name,key=self.get_description())
        elif(ff=="xlsx"):
            w=pd.ExcelWriter(tf.name)
            self.get_dataframe().to_excel(w)
            w.save()
        elif(ff=="json"):
            self.get_dataframe().to_json(tf.name)
        elif(ff=="feather"):
            self.get_dataframe().to_feather(tf.name)
        elif(ff=="stata"):
            self.get_dataframe().to_stata(tf.name)
        elif(ff=="msgpack"):
            self.get_dataframe().to_msgpack(tf.name)
        else:
            raise ValueError('%s is not a valid file format.' % (ff))
        return tf
    
class SingleProcessDataframeMixin(object):
    def get_dataframe(self):
        return get_model_dataframe(self.model,self.request.session['params'])

class SingleProcessDataframeFormView(SessionWizardView):
    template_name = "actions/output/dataframe/single/single_form.html"

    def get_context_data(self,**kwargs): 
        context = super(SingleProcessDataframeFormView, self).get_context_data(**kwargs)
        context['model_name']=self.model.__name__
        return context

    def get_form_kwargs(self, step):
        if step == 'step_one' :
            return {'user': self.request.user}
        elif step == 'step_two' : # selects batch
            return {'process':self.get_cleaned_data_for_step('step_one').get('process')}
        elif step == 'step_three': # selects limits
            return {'batches':self.get_cleaned_data_for_step('step_two').get('batches')}
        else:
            return {}
    
    def done(self,form_list,**kwargs):
        params={}
        for form in form_list:
            params.update(form.cleaned_data)
        self.request.session['params']=params
        return HttpResponseRedirect(reverse(self.download_url_name))

class HistorianImporterFormView(SessionWizardView):
    template_name = "actions/input/historian/historian_form.html"

    def get_form_kwargs(self, step):
        if step == 'step_one': #selects process
            return {'user': self.request.user}
        elif step == 'step_two' : # selects batch
            return {'process':self.get_cleaned_data_for_step('step_one').get('process')}
        elif step == 'step_three': # selects limits
            return {'batch':self.get_cleaned_data_for_step('step_two').get('batch')}
        elif step == 'step_four': # selects endpoints
            return {'user':self.request.user}
        elif step == 'step_five': # selectes nodes
            return {'endpoints':self.get_cleaned_data_for_step('step_four').get('endpoints')}
        else:
            return {}

    def get_context_data(self,**kwargs):
        context = super(SessionWizardView,self).get_context_data(**kwargs)
        context['model_name']=self.model.__name__
        return context

    def done(self,form_list,**kwargs):

        params={}
        for form in form_list:
            params.update(form.cleaned_data)

        results=OPCUAHistorianImporter(self.request.user,self.model,params)        
        
        context={}
        context['results'] = results
        context['model_name'] = self.model.__name__

        template = 'actions/input/historian/historian_importer.html'

        return TemplateResponse(self.request, [template], context)