
from opcua.client.client import Client

from BioPyApp.resources import ClassResource, EventResource, VariableResource
from opcua.crypto import security_policies
from opcua.ua import MessageSecurityMode

def EndpointClient(endpoint):
    ec = Client(endpoint.url)
    pol=getattr(security_policies,"SecurityPolicy"+endpoint.policy)
    mod=getattr(MessageSecurityMode,endpoint.mode)
    ec.set_security(pol, 
                    endpoint.certificate, 
                    endpoint.private_key,
                    server_certificate_path=endpoint.server_certificate,
                    mode=mod)
    return ec        


def OPCUAHistorianVariablesNodeRead(client,start,end,node):
    return client.get_node(node.nodeid).read_raw_history(start,end)

def OPCUAHistorianVariablesNodesReader(batch,start,end,endpoint,nodes):
    rows={}
    client=EndpointClient(endpoint)
    for node in nodes:
        rows += OPCUAHistorianVariablesNodeRead(client,start,end,node)
    client.disconnect()
    return rows

def OPCUAHistorianVariablesDataset(params):
    dataset=[]
    for endpoint in params.endpoints:
        endpoint_nodes = [node for node in params.nodes if (node.type=="variables" and node.endpoint==endpoint)]
        dataset += OPCUAHistorianVariablesReader(params.batch,params.start,params.end,endpoint,endpoint_nodes)
    
    return dataset

def OPCUAHistorianEventsDataset(params):
    dataset=[]
    for endpoint in params.endpoints:
        endpoint_nodes = [node for node in params.nodes if (node.type=="events" and node.endpoint==endpoint)]
        dataset += OPCUAHistorianEventsReader(params.batch,params.start,params.end,endpoint,endpoint_nodes)
    
    return dataset

def OPCUAHistorianClassesDataset(params):
    dataset=[]
    for endpoint in params.endpoints:
        endpoint_nodes = [node for node in params.nodes if (node.type=="classes" and node.endpoint==endpoint)]
        dataset += OPCUAHistorianClassesReader(params.batch,params.start,params.end,endpoint,endpoint_nodes)
    
    return dataset
    
def OPCUAHistorianDatasets(params):
    """
    From a set of parameters, the corresponding datasets
    for the different variables are produced.
    """
    datasets={}
    d_v = OPCUAHistorianVariablesDataset(params)
    d_e = OPCUAHistorianEventsDataset(params)
    d_c = OPCUAHistorianClassesDataset(params)
    if(d_v):
        datasets['variables']=d_v
    if(d_e):
        datasets['events']=d_e
    if(d_c):
        datasets['classes']=d_c
    return datasets

def OPCUAHistorianResults(datasets,user):
    """
    From a set of datasets of the different variables,
    the corresponding results of importation are produced.
    """
    results={}
    if(datasets['variables']):
        results['variables']=VariableResource(user).import_data(
                                          datasets['variables'],
                                          dry_run=True,
                                          raise_errors=False,
                                          user=user)
    if(datasets['events']):
        results['events']=EventResource(user).import_data(
                                          datasets['events'],
                                          dry_run=True,
                                          raise_errors=False,
                                          user=user)
    if(datasets['classes']):
        results['classes']=ClassResource(user).import_data(
                                          datasets['classes'],
                                          dry_run=True,
                                          raise_errors=False,
                                          user=user)
    
    return results

test