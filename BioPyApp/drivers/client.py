
from urllib.parse import urlparse
from opcua.client.client import Client, Shortcuts
from opcua.client.ua_client import UaClient
from opcua.crypto import security_policies
from opcua.ua import MessageSecurityMode, SecurityPolicy

class EndpointClient(Client):
    '''
    Wrapper for the connection of endpoint. Does not need to call .connect().
    '''
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
        self.connect()

    def safe_disconnect(self):
        try:
            self.disconnect()
        except:
            pass