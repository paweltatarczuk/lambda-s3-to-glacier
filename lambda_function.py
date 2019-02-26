#!/usr/bin/env python3
import boto3
import os
import re
import time

response = []
start_time = time.time()

bucket = os.environ['BUCKET_NAME']
timeout = int(os.environ['TIMEOUT']) if 'TIMEOUT' in os.environ else 30

s3 = boto3.client('s3')

def process_objects(continue_token=''):
    args = {'Bucket': bucket}
    if continue_token:
        args['ContinuationToken'] = continue_token
    objects = s3.list_objects_v2(**args)

    for obj in objects['Contents']:
        if obj['StorageClass'] != 'STANDARD':
            response.append('Skipping %s - not a STANDARD storage class' % (obj['Key'],))
            continue

        if obj['Size'] <= 128000:
            response.append('Skipping %s - smaller than 128KB' % (obj['Key'],))
            continue

        if re.search(r'\.manifest(\.gpg)?$', obj['Key']):
            response.append('Skipping %s - manifest file' % (obj['Key'],))
            continue

        response.append('Moving %s to GLACIER storage class' % (obj['Key'],))
        s3.copy(
            {
                'Bucket': bucket,
                'Key': obj['Key']
            },
            bucket,
            obj['Key'],
            ExtraArgs = {
                'StorageClass': 'GLACIER',
                'MetadataDirective': 'COPY'
            }
        )

        if time.time() - start_time >= timeout:
            print('Timeout - stopping function, transition will continue in next run')
            return

    if 'NextContinuationToken' in objects:
        process_objects(objects['NextContinuationToken'])

def lambda_handler(event, context):
    err = None

    try:
        process_objects()
    except Exception as e:
        err = str(e)
    return {
        'status': 500 if err else 200,
        'lines': response,
        'error': err
    }
