import django_pandas as dp
import pandas as pd


def get_model_dataframe(model,params):
    #assign parameters
    batches = params['batches']
    predictors = params['predictors']
    unfolding = params['unfolding_method']
    axis = params['unfolding_axis']
    compression = params['compression']
    time = params['time_reference']

    #generate queryset
    qs = model.objects.filter(batch__in=batches,name__in=predictors)

    #make dataframe
    bfn =[time,"name","value"]
    
    if(unfolding=="idx"):
        bfn.extend(["id","batch__id"])
        df = qs.to_pivot_table(values="value",fieldnames=bfn,rows=["id","batch__id",time],cols="name")

    elif(unfolding=="ts"):
        bfn.append("batch__id")
        df = qs.to_timeseries(index=time,fieldnames=bfn,values="value",pivot_columns="name",storage="long")
    
    elif(unfolding=="bw_tv"):
        bfn.append("batch__id")
        df = qs.to_pivot_table(fieldnames=bfn,values="value",rows="batch__id",cols=[time,"name"])

    elif(unfolding=="bw_vt"):
        bfn.append("batch__id")
        df = qs.to_pivot_table(fieldnames=bfn,values="value",rows="batch__id",cols=["name",time])

    elif(unfolding=="vw_tb"):
        bfn.append("batch__id")
        df = qs.to_pivot_table(fieldnames=bfn,values="value",rows="name",cols=[time,"batch__id"])

    elif(unfolding=="vw_bt"):
        bfn.append("batch__id")
        df = qs.to_pivot_table(fieldnames=bfn,values="value",rows="name",cols=["batch__id",time])

    elif(unfolding=="tw_bv"):
        bfn.append("batch__id")
        df = qs.to_pivot_table(fieldnames=bfn,values="value",rows=time,cols=["batch__id","name"])

    elif(unfolding=="tw_vb"):
        bfn.append("batch__id")
        df = qs.to_pivot_table(fieldnames=bfn,values="value",rows=time,cols=["name","batch__id"])

    else:
        raise ValueError(unfolding+" is not a valid unfolding method.")

    #transpose (if required)
    if(axis=="y"):
        df = df.transpose()

    #compress dataframe
    if(compression=="sparse"):
        df = df.to_sparse()
    elif(compression=="dense"):
        df = df.to_dense()
    else:
        raise ValueError(str(compression)+' is not a valid compression method.')

    return df