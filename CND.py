import hashlib
import argparse
import time

parser = argparse.ArgumentParser(description="Let's go Nonce hunting!")
parser.add_argument('d_val', metavar='D', type=int, #nargs='+',
                    help='Number of leftmost 0 bits')
args = parser.parse_args()

block = 'COMSM0010cloud'
D = args.d_val

begin = time.time()

for nonce in range(0, 4294967296):
    blockandnonce = block + str(nonce)
    hashValue = hashlib.sha256(blockandnonce.encode()).hexdigest()
    binary = bin(int(hashValue, 16))[3:]

    if(int(binary[0:D]) == 0):
        termination = time.time()
        elapsed_time = termination - begin

        print(binary + "\n")
        print('%.5f'%elapsed_time + " secs taken")
        break

