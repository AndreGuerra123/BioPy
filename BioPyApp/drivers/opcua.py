
from urllib.parse import urlparse
from opcua.client.client import Client, UaClient, Shortcuts
from opcua.crypto import security_policies
from opcua.ua import MessageSecurityMode, SecurityPolicy
from BioPyApp.resources import ClassResource, EventResource, VariableResource
from BioPyApp.models import Variable, Event, Class

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
        
def OPCUAHistorianReader(params):
    start = params['start']
    end = params['end']
    endpoints = params['endpoints']
    nodes = params['nodes']

    rows={}
    for endpoint in endpoints:
        client=endpoint.get_client()
        for node in nodes:
            if node.endpoint == endpoint:
                rows += client.get_node(node.nodeid).read_raw_history(start,end)
        client.disconnect()
    return rows

def OPCUAVariableHistorianDataset(params):
    rows = OPCUAHistorianReader(params)

    #dataset must have process, batch, name, value, timestamp...everything else is acessory.
    print(rows)
    
    return rows
    
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

