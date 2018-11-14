from BioPyApp.resources import ClassResource, EventResource, VariableResource
from BioPyApp.models import Variable, Event, Class


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

