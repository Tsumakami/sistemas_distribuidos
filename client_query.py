import threading, time, socket, logging, json
from models.client import Client
from models.server import Server
from models.machine import Machine
from typing import List

logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='logs/tome_falha.log', level=logging.DEBUG)

TIMEOUT = 2

MASTER_PORT = 7380
SLAVE_PORT = (7300, 7302)
SERVER_IP = "127.0.0.1"
           
class SlaveMachine(Machine):
    product_list_ids: List[str]
    product_list_names: List[str]
    request_names: str
    response: dict

    def __init__(self, name, port, slave_port, ip):
        self.product_list_ids = list()
        self.product_list_names = list()
        self.request_names = ''
        self.response = {}
        super().__init__(name, port, slave_port, ip)

    def execute_machine(self):
        try:
            self.recv_message()

        except Exception as e:
            logging.error(f'{self.name} - Error: {e}')

    def task(self, slave_port):
        port_destination = slave_port

        while True:
            try:
                
                self.get_client().init_client_socket()

                self.get_client().send_message(request, port_destination)
                self.listen_response()
            except: 
                print('Server not found.\n')
            
    def listen_response(self):
        
        resp = self.get_client().client.recv(1024)
        print(resp.decode('utf-8'))

    def recv_message(self, bytes_recv:int) -> None:
        server = self.get_server().server
        server.listen(10)
        
        try:
            while True:
                conn, addr = server.accept()
                
                logging.info(f'{self.name} - conn{conn}, addr={addr}')

                resp = conn.recv(bytes_recv).decode()
                is_ok = self.controll_messages(conn, addr, resp.strip())

                if is_ok is False:
                    logging.info(f'{self.name} - Exit application')
                    
                    return False

        except Exception as e:
            logging.error(f'{self.name} - Fail to receiv message. Error={e}')
            self.get_server().disconnect()

    def controll_messages(self, conn: socket, addr, response: str) -> bool:
        not_is_null = response != None and response != ''

        thread_listen_message = threading.Thread(target=self.task, name='Dc_Server', args=(self.slave_port[0],))
        

        thread_listen_message_store = threading.Thread(target=self.task, name='Store_Server', args=(self.slave_port[1],))
        
        if not_is_null:
            logging.info(f'{self.name} - Receiving message: {response.strip()}')


            if 'list' in response:
                thread_listen_message.start()

                list_products = self.list_products()

                logging.info(f'{self.name} - Processing response: {response.strip()}, result is a produt list.')

                logging.info(f'{self.name} -  send list all products: {(skuId for skuId in list_products)} to addr: {addr}')

                conn.send('Available Products:\n'.encode('utf-8'))

                for product in list_products:
                    message = f'{product.productId}: {product.productName}\n'
                    conn.send(message.encode('utf-8'))

            elif response in self.product_list_ids:
                thread_listen_message.start()
                thread_listen_message_store.start()
                
                product = self.get_product_by_id(response)
                
                product_json = json.dumps(product._asdict()) + '\n'

                conn.send(product_json.encode('utf-8'))

            elif 'work?' in response:
                conn.send('Are Working...'.encode('utf-8'))

            else:
                logging.warning("Invalid request.")
                conn.send("Invalid request.".encode('utf-8'))

            conn.close()
        
        return True
    


def execute_thread(index: int, machine: Machine):
    thread = threading.current_thread()
    logging.info(f'{thread.name} - Start thread.')

    machine.execute_machine()

if  __name__ == "__main__" :

    slave = SlaveMachine('Slave', SLAVE_PORT, MASTER_PORT, SERVER_IP)

    threadSlave = threading.Thread(target=execute_thread, name="Slave", args=(1, slave))
    
    threadSlave.start()
