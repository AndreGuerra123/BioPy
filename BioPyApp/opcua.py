
from urllib.parse import urlparse
from opcua.client.client import Client, UaClient, Shortcuts
from opcua.crypto import security_policies
from opcua.ua import MessageSecurityMode, SecurityPolicy
from .resources import ClassResource, EventResource, VariableResource

class OPCUAClient(Client):
    def __init__(self,endpoint):
        self.server_url = urlparse(endpoint.url)
        self._username = self.server_url.username
        self._password = self.server_url.password
        self.name = "BioPy OPCUA Client"
        self.description = self.name
        self.application_uri = "urn:biopy:client"
        self.product_uri = "urn:biopy.com:client"
        self.secure_channel_id = None
        self.secure_channel_timeout = 3600000
        self.session_timeout = 3600000 
        self._policy_ids = []
        self.user_certificate = None
        self.user_private_key = None
        self._server_nonce = None
        self._session_counter = 1
        self.keepalive = None
        self.max_messagesize = 0  
        self.max_chunkcount = 0 
        if endpoint.policy:
            self.set_security(getattr(security_policies,"SecurityPolicy"+endpoint.policy),
                    endpoint.certificate.path,
                    endpoint.private_key.path,
                    server_certificate_path=endpoint.server_certificate.path,
                    mode=getattr(MessageSecurityMode,endpoint.mode))
        else:
            self.security_policy = SecurityPolicy()

        self.uaclient = UaClient(endpoint.timeout)
        self.nodes = Shortcuts(self.uaclient)
        
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
