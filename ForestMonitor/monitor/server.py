import socket
from queue import Queue
from threading import Thread, Lock
from lib.sensor_status import SensorService


SEND_REQUEST = "START_SEND"
STOP_REQUEST = "STOP_SEND"

class ClientMetaInfo:
    def __init__(self, address, queue, id=-1):
        self.address = address
        self.queue = queue
        self.id = id

class MonitorServer:
    _host = socket.gethostname()
    _port = 2004
    _send_request_lock = Lock()
    
    def __init__(self, sensor_service:SensorService):
        self.sensor_service = sensor_service
        self.list_of_clients = []
        self.monitor_image = open("monitor/__demo/empty-image.jpg", "rb").read()


    def make_request_from_client(self, client_id, request):
        for client in self.list_of_clients:
            if (client.id == client_id):
                if request==SEND_REQUEST: self.stop_all_sending() # TODO Hacky, refactor
                client.queue.put(request)
        
    
    def reset_send_request(self):
        self.send_request_id = -1


    def multi_threaded_client(self, connection, client_info:ClientMetaInfo):
        connection.send(str.encode('Server is working:'))
        current_status = None
        while True:
            #Check if any messages from app:    
            try:
                req = client_info.queue.get_nowait()
            except:
                req = ''
            
            try:
                #Check for data from client
                data = connection.recv(3)
                
                message_type = data.decode('utf-8')
                if(message_type=="INF"):
                    client_message = connection.recv(500).decode('utf-8')
                    # Update the current status
                    current_status = self.sensor_service.parse_status(client_message)

                elif (message_type=="IMG"):
                    self.monitor_image = connection.recv(500000)
                
                response = "OK"
                if current_status is not None:
                    # Bind an id to our meta address
                    if client_info.id == -1:
                        client_info.id = int(current_status.sensor_id)

                    # Manage any request to client
                    if req != '': 
                        response = ",".join([response, req])
                
                connection.sendall(str.encode(response))
            except Exception as e:
                self.sensor_service.reset_status(current_status)
                print(e)
                break
        connection.close()

    def run_info_server(self):
        ServerSideSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ServerSideSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ThreadCount = 0

        try:
            ServerSideSocket.bind((self._host, self._port))
        except socket.error as e:
            exit()

        print('Socket is listening..')
        ServerSideSocket.listen(5)

        try:    
            while True:
                Client, address = ServerSideSocket.accept()
                new_client_queue = Queue(maxsize=5)
                new_client_info = ClientMetaInfo(address, new_client_queue)
                self.list_of_clients.append(new_client_info)
                
                new_thread = Thread(target=self.multi_threaded_client, args=(Client, new_client_info, ))
                ThreadCount += 1
                new_thread.start()
                
        except socket.error as e:
            print(f"SERVER EXCEPTION : {str(e)}")
        finally:
            ServerSideSocket.close()

    def get_all_sensor_stats(self):
        return self.sensor_service.get_all_sensor_stats()
    
    def get_sensor_stats(self, id):
        return self.sensor_service.get_sensor_stats(id)
    
    def get_monitor_image(self):
        return self.monitor_image
    
    def stop_all_sending(self):
        for client in self.list_of_clients:
            self.make_request_from_client(client.id, STOP_REQUEST)

if __name__ == "__main__":
    def test_request(ms):
        import time
        for i in range(10):
            time.sleep(5)
            ms.make_request_from_client(3, STOP_REQUEST)
            ms.make_request_from_client(3, SEND_REQUEST)
            time.sleep(5)
            ms.make_request_from_client(3, STOP_REQUEST)

    sensor_service = SensorService()
    ms = MonitorServer(sensor_service)
    test_thread = Thread(target=test_request, args=(ms, ))
    test_thread.start()
    ms.run_info_server()
    