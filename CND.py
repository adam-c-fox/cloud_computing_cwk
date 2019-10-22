import hashlib
import argparse
import time

parser = argparse.ArgumentParser(description="Let's go Nonce hunting!")
parser.add_argument('d_val', metavar='D', type=int, help='Number of leftmost 0 bits')
args = parser.parse_args()

block = 'COMSM0010cloud'
D = args.d_val

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
        break
