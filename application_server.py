import threading, time, socket, logging, json, os
from models.product import Product
from models.machine import Machine
from typing import List
from collections import namedtuple

logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='logs/application_server.log', level=logging.DEBUG)
CMD_LISTEN_LOG = 'tail -f logs/application_server.log'

TIMEOUT = 2

MY_PORT = 7380
SERVER_PORTS = (7300, 7302)
SERVER_IP = "127.0.0.1"
           
class ApplicationMachine(Machine):
    product_list_ids: List[str]
    product_list_names: List[str]
    request_names: str
    response: str

    def __init__(self, name, port, slave_port, ip):
        self.product_list_ids = list()
        self.product_list_names = list()
        self.request_names = ''
        self.response = {}
        super().__init__(name, port, slave_port, ip)

    def execute_machine(self):
        try:
            self.get_server().start_socket()

            self.set_product_list_ids()

            self.recv_message(1024)

        except Exception as e:
            logging.error(f'{self.name} - Error: {e}')

    def task(self, request, slave_port):
        port_destination = slave_port

        try:
            
            self.get_client().init_client_socket()

            self.get_client().send_message(request, port_destination)
            self.listen_response()
        except: 
            print('Server not found.\n')

    def set_product_list_ids(self) -> None:
        product_list = self.list_products()

        for product in product_list:
            self.product_list_ids.append(product.productId)
            
    def listen_response(self):
        resp = self.get_client().client.recv(1024)
        print('resp:', resp)
        self.response[threading.current_thread().name] = resp.decode()

    def recv_message(self, bytes_recv:int) -> None:
        server = self.get_server().server
        server.listen(10)
        
        try:
            while True:
                conn, addr = server.accept()
                

                request = conn.recv(bytes_recv).decode()
                
                logging.info(f'{self.name} - Receive request: {request} conn: {conn}, addr: {addr}')
                
                is_ok = self.controll_request(conn, addr, request.strip())

                if is_ok is False:
                    logging.info(f'{self.name} - Exit application')
                    
                    return False
            
        except Exception as e:
            logging.error(f'{self.name} - Fail to receiv message. Error={e}')
            self.get_server().disconnect()

    def controll_request(self, conn: socket, addr, request: str) -> bool:

        try:
            if 'list' in request:
                products = self.list_products()

                message = 'Available Products:\n'
                for product in products:
                    message = message + f'ProductId: {product.productId}: {product.productName} - Sale Price: {product.salePrice}\n'

                conn.send(message.encode('utf-8'))

            elif request in self.product_list_ids:
                thread_listen_message = threading.Thread(target=self.task, name='Dc_Server', args=(request, self.slave_port[0]))
                thread_listen_message_store = threading.Thread(target=self.task, name='Store_Server', args=(request, self.slave_port[1]))
            
                thread_listen_message.start()
                time.sleep(TIMEOUT)
                thread_listen_message_store.start()
                time.sleep(TIMEOUT)

                logging.info(f'{self.name} - Receive message={self.response}')

                if self.response != None:
                    product = None
                    additional_info_dc = ''
                    additional_info_store = ''
                    has_dc = thread_listen_message.name in self.response
                    has_store = thread_listen_message_store.name in self.response

                    if has_dc:
                        dc = json.loads(self.response[thread_listen_message.name].strip())
                        product = dc
                        additional_info_dc = f' Distribution Center: {product["availableStock"]}\n'

                    if has_store:
                        store = json.loads(self.response[thread_listen_message_store.name].strip())
                        product = store
                        additional_info_store = f' Stock in Store: {product["cdsWithStock"]}\n'
                    
                    product_info = f'Product Info\n Product Id: {product["productId"]}\n Prodcut Name: {product["productName"]}\n Sale Price: {product["salePrice"]}\n'
                                        
                    product_info = product_info + additional_info_dc + additional_info_store
                    
                conn.send(product_info.encode('utf-8'))

            elif 'work?' in request:
                conn.send('Are Working...'.encode('utf-8'))

            else:
                logging.warning("Invalid request.")
                conn.send("Invalid request.".encode('utf-8'))

        except Exception as e:
            logging.error(f'{self.name} - Application crashed. Error={e.with_traceback()}')
            self.get_server().disconnect()

        conn.close()

        return True

    def list_products(self) -> List[Product]:
        json_db = self.access_db()

        product_list = list()
        try:
            for json_product in json_db:
                product = namedtuple("ProductStores",  json_product.keys())(*json_product.values())

                logging.debug(f"{self.name} - Product Id: {product.productId}, List Price: {product.listPrice}, Sale Price: {product.salePrice}, Name Product: {product.productName}")

                product_list.append(product)
        except Exception as e:
            logging.error(f'{self.name} - Fail to get product list. Error={e}')
            self.get_server().disconnect()

        return product_list       

    
    def access_db(self) -> json:
        json_file = open('DB/application.json', 'r')
        return json.load(json_file)


def execute_thread(index: int, machine: Machine):
    thread = threading.current_thread()
    logging.info(f'{thread.name} - Start thread.')

    machine.execute_machine()

if  __name__ == "__main__" :

    application = ApplicationMachine('Slave', MY_PORT, SERVER_PORTS, SERVER_IP)

    threadSlave = threading.Thread(target=execute_thread, name="Slave", args=(1, application))
    
    threadSlave.start()

    os.system(CMD_LISTEN_LOG)
