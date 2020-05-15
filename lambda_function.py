import json
from sms_spam_classifier_utilities import one_hot_encode
from sms_spam_classifier_utilities import vectorize_sequences
import boto3
from io import BytesIO
import email

def lambda_handler(event, context):
    # TODO implement
    print(event)
    test_messages = read_from_s3()
    
    #test_messages = ["FreeMsg: Txt: CALL to No: 86888 & claim your reward of 3 hours talk time to use from your phone now! ubscribe6GBP/ mnth inc 3hrs 16 stop?txtStop"]
    one_hot_test_messages = one_hot_encode(test_messages, 9013)
    encoded_test_messages = vectorize_sequences(one_hot_test_messages, 9013)
    print(encoded_test_messages)
    payload = json.dumps(encoded_test_messages.tolist())
    lo = payload.strip('[')
    lo = lo.strip(']')
    
    endpoint_name = 'sms-spam-classifier-ll-2020-05-07-07-24-58-952'
    runtime = boto3.Session().client(service_name='sagemaker-runtime',region_name='us-east-1')
    response = runtime.invoke_endpoint(EndpointName=endpoint_name, ContentType='text/csv', Body=lo)
    result = json.loads(response['Body'].read().decode())
    res = result['predictions']
    print(res)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    
def read_from_s3():
    session = boto3.Session()
    s3_client = session.client("s3")
    f = BytesIO()
    #s3_client.download_fileobj('emailstoragehw4', 'k8dku3o133hpiuou679jc08emd91upitdvh70jg1', f)
    s3_client.download_file('emailstoragehw4', 'k8dku3o133hpiuou679jc08emd91upitdvh70jg1', '/tmp/k8dku3o133hpiuou679jc08emd91upitdvh70jg1')
    #f.seek(0)
    #k  = f.getvalue()
    f = open("/tmp/k8dku3o133hpiuou679jc08emd91upitdvh70jg1", "r")
    k = f.read()
    b =  email.message_from_string(k)
    body = ""
    
    if b.is_multipart():
        for part in b.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))
    
            # skip any text/plain (txt) attachments
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True)  # decode
                break
    # not multipart - i.e. plain text, no attachments, keeping fingers crossed
    else:
        body = b.get_payload(decode=True)
    
    #print(body)
    emailbody = body.decode("utf-8")
    test_messages = []
    test_messages.append(emailbody)
    return test_messages
