from BioPyApp.resources import ClassResource, EventResource, VariableResource
from BioPyApp.models import Variable, Event, Class
import tablib


def OPCUAHistorianReader(params):
    start = params['start']
    end = params['end']
    endpoints = params['endpoints']
    nodes = params['nodes']

    hist_list=[]
    for endpoint in endpoints:
        client=endpoint.get_client()
        for node in nodes:
            if node.endpoint == endpoint:
                hist_list += client.get_node(node.nodeid).read_raw_history(start,end)
        client.disconnect()
    return hist_list

def OPCUAVariableHistorianDataset(params):
    hist_list = OPCUAHistorianReader(params)
    print(hist_list)
    data = tablib.Dataset()
    data.headers = ('process', 'batch','name','timestamp','value')
    for row in hist_list():
        data.append((params['process'],params['batch'],node.name,node.timestamp,node.value))   
    return data
    
def OPCUAHistorianImporter(user,model,params):
    if(model == Variable):
        return VariableResource(user).import_data(
                                          OPCUAVariableHistorianDataset(params),
                                          dry_run=True,
                                          raise_errors=False,
                                          user=user)
    elif(model == Event):
        return EventResource(user).import_data(
                                          OPCUAEventHistorianDataset(params),
                                          dry_run=True,
                                          raise_errors=False,
                                          user=user)
    elif(model == Class):
        return ClassResource(user).import_data(
                                          OPCUAClassHistorianDataset(params),
                                          dry_run=True,
                                          raise_errors=False,
                                          user=user)
    else:
        raise ValueError(str(model) + " is not a valid historian model.")

