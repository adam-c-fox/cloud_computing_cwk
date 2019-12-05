import json
import time
import hashlib

def lambda_handler(event, context):
    d = event["queryStringParameters"]
    
    if 'd' not in d:
        return {
            'statusCode': 400,
            'body': json.dumps("No d value specified.")
        }
        
    block = 'COMSM0010cloud'
    D = int(d["d"])
    begin = time.time()
    
    for nonce in range(0, 4294967296):
        blockandnonce = block.encode('utf-8') + nonce.to_bytes(4, byteorder='big')
        hashValue = hashlib.sha256(hashlib.sha256(blockandnonce).digest()).hexdigest()
        binary = bin(int(hashValue, 16))[2:].zfill(256)
    
        if(int(binary[0:D]) == 0):
            termination = time.time()
            elapsed_time = termination - begin
            print(nonce)
            print('%.10f' % elapsed_time + ' secs')
            data = [binary, nonce, elapsed_time]
            return {
                'statusCode': 200,
                'body': json.dumps(data)
            }
            break
    
    
