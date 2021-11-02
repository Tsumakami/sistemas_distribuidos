from socket import socket
import threading, logging, os, json
from typing import List
from collections import namedtuple
from models.machine import Machine
from models.stores import Stores

logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='logs/store_service.log', level=logging.DEBUG)
CMD_LISTEN_LOG = 'tail -f logs/store_service.log'

TIMEOUT = 2
MAX_REQUESTS = 15
MAX_EXECUTION = 50

SERVER_IP = '127.0.0.1'
SERVER_PORT = 7302

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
        product_list = self.product_list()

        for product in product_list:
            self.product_list_ids.append(product.productId)

    def access_db(self) -> json:
        json_file = open('DB/stores.json', 'r')
        return json.load(json_file)

    def product_list(self) -> List[Stores]:
        json_db = self.access_db()

        product_list = list()
        try:
            for json_product in json_db:
                product_stores = namedtuple("Stores",  json_product.keys())(*json_product.values())
                #print("ProductId: ", stores.productId, "\nSkuId", stores.skuId, "\nEstoque Disponível: ", stores.availableStock, "\nListPrice: ", stores.listPrice, "\nSalePrice: ", stores.salePrice, "\nProductName: ", stores.productName, "\nLojas com Estoque: ", stores.cdsWithStock)
                logging.info(f" ProductId: {product_stores.productId}\n SkuId: {product_stores.skuId}\n Estoque Disponível: {product_stores.availableStock}\n listPrice: {product_stores.listPrice}\n SalePrice: {product_stores.salePrice}\n Nome do Produto: {product_stores.productName}\n Cidades com Estoque: {product_stores.cdsWithStock}\n")
                product_list.append(product_stores)
        except Exception as e:
            logging.error(f'{self.name} - Fail to get product list. Error={e}')
            self.get_server().disconnect()

        return product_list

    def get_product_by_id(self, productId: str) -> Stores:
    
         try:
             product_store_list = self.product_list()
    
             for product_store in product_store_list:
                 if productId == product_store.productId:
                     return product_store
         except Exception as e:
             logging.error(f'{self.name} - Fail to get product store info by productId: {productId}. Error={e}')
             self.get_server().disconnect()

    def controll_messages(self, conn: socket, addr, response: str) -> bool:
        not_is_null = response != None and response != ''

        if not_is_null:
            logging.info(f'{self.name} - Receiving message: {response.strip()}')

            if 'list' in response:
                product_store_list = self.product_list()

                logging.info(f'{self.name} - Processing response: {response.strip()}, result is a store list.')

                logging.info(f'{self.name} -  send list all products: {(product for product in product_store_list)} to addr: {addr}')

                conn.send('Available Products:\n'.encode('utf-8'))
                for product in product_store_list:
                    message = f" ProductId: {product.productId}: {product.productName}\nCity with stock: {product.cdsWithStock}\n"
                    conn.send(message.encode('utf-8'))

            elif response in self.product_list_ids:
                product_store = self.get_product_by_id(response)

                product_store_json = json.dumps(product_store._asdict()) + '\n'

                conn.send(product_store_json.encode('utf-8'))

            elif 'work?' in response:
                conn.send('Are Working...'.encode('utf-8'))

            else:
                print("Invalid search.")

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
    server = ServerMachine('Server', SERVER_PORT, 0000, SERVER_IP)

    threadServer = threading.Thread(target=execute_thread, name="Server", args=(0, server))

    threadServer.start()
