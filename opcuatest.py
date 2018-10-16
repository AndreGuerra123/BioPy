from opcua import ua
from opcua.client.ua_client import UaClient

if __name__ == "__main__":
    client = UaClient(timeout=10)
    client.get_endpoints()
    