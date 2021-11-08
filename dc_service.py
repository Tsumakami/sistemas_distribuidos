from socket import socket
import threading, logging, os, json
from typing import List
from collections import namedtuple
from models.machine import Machine
from models.product import Product

logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='logs/dc_server.log', level=logging.DEBUG)
CMD_LISTEN_LOG = 'tail -f logs/dc_server.log'

TIMEOUT = 2
MAX_REQUESTS = 15
MAX_EXECUTION = 50

SERVER_IP = '127.0.0.1'
SERVER_PORT = 7300

class ServerMachine(Machine):
    product_list_ids: List[str]

    def __init__(self, name, port, slave_port, ip):
        self.product_list_ids = list()
        super().__init__(name, port, slave_port, ip)

    def execute_machine(self) -> None:
        try:
            self.get_server().start_socket()

            self.set_product_list_ids()

            thread_listen_message = threading.Thread(target=self.recv_message, name='Listen_Server', args=(1024,))
            thread_listen_message.start()

            os.system(CMD_LISTEN_LOG)

        except Exception as e:
            logging.error(f'{self.name} - Error: {e}')
    
    def set_product_list_ids(self) -> None:
        product_list = self.list_products()

        for product in product_list:
            self.product_list_ids.append(product.productId)

    def get_product_list_ids(self) -> List[str]:
        return self.product_list_ids

    def access_db(self) -> json:
        json_file = open('DB/dc.json', 'r')
        
        json_result = json.load(json_file)
        
        json_file.close()

        return json_result

    def list_products(self) -> List[Product]:
        json_db = self.access_db()

        list_products = list()
        try:            
            for json_product in json_db:
                product = namedtuple("Product",  json_product.keys())(*json_product.values())
                
                list_products.append(product)
        except Exception as e:
            logging.error(f'{self.name} - Fail to get product list. Error={e}')
            self.get_server().disconnect()

        return list_products

    def get_product_by_id(self, productId: str) -> Product:
        
        try:
            list_products = self.list_products()

            for product in list_products:
                if productId == product.productId:
                    return product
        except Exception as e:
            self.get_server().disconnect()

    def controll_messages(self, conn: socket, addr, response: str) -> bool:
        not_is_null = response != None and response != ''

        if not_is_null:
            logging.info(f'{self.name} - Receiving message: {response.strip()}')

            if 'list' in response:
                list_products = self.list_products()

                logging.info(f'{self.name} - Processing response: {response.strip()}, result is a produt list.')

                logging.info(f'{self.name} -  send list all products: {(skuId for skuId in list_products)} to addr: {addr}')

                conn.send('Available Products:\n'.encode('utf-8'))

                for product in list_products:
                    message = f'{product.productId}: {product.productName}\n'
                    conn.send(message.encode('utf-8'))

            elif response in self.product_list_ids:
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

def execute_thread(index: int, machine: Machine):
    thread = threading.current_thread()
    logging.info(f'{thread.name} - Start thread.')

    machine.execute_machine()

if  __name__ == "__main__" :
    server = ServerMachine('DC Server', SERVER_PORT, (None, None), SERVER_IP)    
    
    threadServer = threading.Thread(target=execute_thread, name="Server", args=(0, server))
    
    threadServer.start()        
