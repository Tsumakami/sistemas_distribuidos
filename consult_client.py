import threading, logging, os, time
from models.machine import Machine


logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='logs/consult_client.log', level=logging.DEBUG)

TIMEOUT = 2
MAX_REQUESTS = 15
MAX_EXECUTION = 50

#SERVER_IP = '10.1.2.122'
SERVER_IP = '127.0.0.1'
MY_PORT = 7304
SERVER_PORT = 7380

class ClientMachine(Machine):

    def execute_machine(self):
        try:
            thread_listen_message = threading.Thread(target=self.task, name='Listen_Server')
            thread_listen_message.start()
            
        except Exception as e:
            logging.error(f'{self.name} - Error: {e}')
    
    def init_message(self):
        message = """
            Consult your wished product:
                help - print this message again
                list - List all products
                [productId] - print all info of the especific product\n
        """
        print(message)

    def task(self):
        port_destination = self.slave_port[0]

        self.init_message()

        while True:
            try:
                request = input()
                
                self.get_client().init_client_socket()

                self.get_client().send_message(request, port_destination)
                self.listen_response()
            except: 
                print('Server not found.\n')
            
    def listen_response(self):
        
        resp = self.get_client().client.recv(1024)
        print(resp.decode('utf-8'))

        #self.get_client().client.close()
        
def execute_thread(index: int, machine: Machine):
    thread = threading.current_thread()
    logging.info(f'{thread.name} - Start thread.')

    machine.execute_machine()

if  __name__ == "__main__" :
    client = ClientMachine('Consult Client', MY_PORT, (SERVER_PORT, None), SERVER_IP)    

    threadServer = threading.Thread(target=execute_thread, name="Client", args=(0, client))
    
    threadServer.start()        
