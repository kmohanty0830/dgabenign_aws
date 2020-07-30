import json
import random
import logging
import time
import tldextract
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

a=['-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '_', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
def encode_fqdn(user_input):
    global a
    dict_features=dict((el,0) for el in a)
    #user_input= fqdn.split('.',1)[0]
    user_input = tldextract.extract(user_input).domain
    list_item=list(user_input)
    x=''
    for i in list_item:
        if i in dict_features:
            dict_features[i] += 1
    for key in dict_features:
        x = x +','+(str(dict_features[key]))
    x= x.strip( ',' )
    return(x)
        
    
def predict_one_dga_value(sm_client, features, endpoint_name):
    # print('Using model endpoint {} to predict dga for this feature vector: {}'.format(endpoint_name, features))
    is_dga = False
    body = features + '\n'
    start_time = time.time()
#     print(features)
    response = sm_client.invoke_endpoint(
                        EndpointName=endpoint_name,
                        ContentType='text/csv',
                        Body=body)
    predicted_value = json.loads(response['Body'].read())
#     print(response['Body'])
#     print(predicted_value)
    duration = time.time() - start_time
    if predicted_value > 0.5:
        is_dga = True
    return is_dga
    
    
    
def lambda_handler(event, context):
    runtime_sm_client = boto3.client(service_name = 'sagemaker-runtime')
    if 'queryStringParameters' not in event:
        # query_params = event['queryStringParameters']
        return {
            'statusCode': 227,
            'body': json.dumps('Invalid Request')
        }
    else:
        query_params = event['queryStringParameters']
        logger.info(msg=query_params)
        ## Predict DGA or not
        features = encode_fqdn(query_params['fqdn'])
        p = predict_one_dga_value(sm_client=runtime_sm_client, features = features, endpoint_name='xgboost-inc-data-endpoint-05-26-2020')
        query_params['dga'] = p
        logger.info(msg=query_params)
        return {
            'statusCode': 200,
            'body': json.dumps(query_params)
        }
