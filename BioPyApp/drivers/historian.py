import tablib
from datetime import timezone
from BioPyApp.resources import ClassResource, EventResource, VariableResource
from BioPyApp.models import Variable, Event, Class

def OPCUAVariableHistorianDataset(params):
    process=params['process']
    batch=params['batch']
    start = params['start']
    end = params['end']
    endpoints = params['endpoints']
    nodes = params['nodes']
    dataset = tablib.Dataset()
    dataset.headers = ('timestamp','process','batch','name','value')

    for endpoint in endpoints:
        client=endpoint.get_client()
        for node in nodes:
            if node.endpoint == endpoint:
                hist = client.get_node(node.nodeid).read_raw_history(start,end)
                for row in hist:
                    dataset.append([row.SourceTimestamp.replace(tzinfo=timezone.utc),process.name,batch.name,node.name,float(row.Value.Value)])
        client.disconnect()
    return dataset
    
def OPCUAEventHistorianDataset(params):
    process=params['process']
    batch=params['batch']
    start = params['start']
    end = params['end']
    endpoints = params['endpoints']
    nodes = params['nodes']

    dataset = tablib.Dataset()
    dataset.headers = ('id','process','batch','name','timestamp','value')

    for endpoint in endpoints:
        client=endpoint.get_client()
        for node in nodes:
            if node.endpoint == endpoint:
                hist = client.get_node(node.nodeid).read_raw_history(start,end)
                for row in hist:
                    dataset.append((None,process.name,batch.name,node.name,row.SourceTimestamp.replace(tzinfo=timezone.utc),float(row.Value.Value)))
        client.disconnect()

    return dataset


def OPCUAClassHistorianDataset(params):
    process=params['process']
    batch=params['batch']
    start = params['start']
    end = params['end']
    endpoints = params['endpoints']
    nodes = params['nodes']
    
    dataset = tablib.Dataset()
    dataset.headers = ('id','process','batch','name','value')

    for endpoint in endpoints:
        client=endpoint.get_client()
        for node in nodes:
            if node.endpoint == endpoint:
                hist = client.get_node(node.nodeid).read_raw_history(start,end)
                for row in hist:
                    dataset.append((None,process.name,batch.name,node.name,str(row.Value.Value)))
        client.disconnect()

    return dataset