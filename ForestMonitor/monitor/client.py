import os
import time
import socket
import random
import datetime
import argparse
from monitor.server import SEND_REQUEST, STOP_REQUEST


host = socket.gethostname()
port = 2004
IMAGE_PATH = "./monitor/__demo/"

def create_and_connect_client():
    ClientMultiSocket = socket.socket()
    try:
        ClientMultiSocket.connect((host, port))
    except socket.error as e:
        print(str(e))
        return None

    return ClientMultiSocket

def get_response(connection):
    return connection.recv(1024).decode('utf-8')

def find_request(resp):
    messages = resp.split(',') 
    
    if (len(messages)>1):
        for msg in messages:
            if msg == SEND_REQUEST:
                return 1
            elif msg == STOP_REQUEST:
                return -1

    return 0

def run_client(sensor_id = 0, start_sending=False, amount_of_messages=5000):
    ClientMultiSocket = create_and_connect_client()
    res = ClientMultiSocket.recv(1024)
    start = time.time()
    messages=0
    is_sending = int(start_sending)
    random.seed(sensor_id)
    location = f'{random.randint(0, 100)},{random.randint(0, 100)}'
    
    
    while messages < amount_of_messages:
        try:
            ts = datetime.timedelta(seconds=round(time.time()-start)) 
            bytes=b''
            CAM_DATA = {"sensor_id": sensor_id, "timestamp":str(ts), "location":location, "status":random.randint(0, 10), "is_sending_image":is_sending}
            print("SENT" + str(CAM_DATA))

            ClientMultiSocket.sendall(str.encode("INF" + str(CAM_DATA)))
            
            res = get_response(ClientMultiSocket)
            if (is_sending > 0):
                image_id = int(sensor_id) if int(sensor_id) < 5 else 1 #Demo reasons, we don't have more than five images
                image_file = open(os.path.join(IMAGE_PATH, f"{image_id}.jpg"), 'rb')

                bytes = image_file.read()
                
                ClientMultiSocket.sendall(str.encode("IMG") + bytes) # Send another message
                res = ','.join([res, get_response(ClientMultiSocket)])
            
            
            if(find_request(res) == 1):
                is_sending = 1
            elif(find_request(res) == -1):
                is_sending = 0
            else:
                pass
            
            print(res)
            messages+=1
            time.sleep(1)
        
        except Exception as e:
            print(e)
            break

    ClientMultiSocket.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-id', '--sensor_id', default=0)           # positional argument
    parser.add_argument('-s', '--start_sending', action='store_true')           # positional argument
    args = parser.parse_args()
    run_client(args.sensor_id, args.start_sending)