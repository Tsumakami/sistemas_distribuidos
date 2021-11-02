from socket import socket
import threading, logging, os, json
from typing import List
from collections import namedtuple
from models.machine import Machine
from models.stores import Stores

logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='logs/dc_server.log', level=logging.DEBUG)
CMD_LISTEN_LOG = 'tail -f logs/dc_server.log'

TIMEOUT = 2
MAX_REQUESTS = 15
MAX_EXECUTION = 50

#SERVER_IP = '10.1.2.122'
SERVER_IP = '127.0.0.1'
SERVER_PORT = 7300

class ServerMachine(Machine):
    stores_list_ids: List[str]

    def execute_machine(self) -> None:
        try:
            self.get_server().start_socket()

            self.set_stores_list_ids()

            thread_listen_message = threading.Thread(target=self.recv_message, name='Listen_Server', args=(1024,))
            thread_listen_message.start()

            #os.system(CMD_LISTEN_LOG)

        except Exception as e:
            logging.error(f'{self.name} - Error: {e}')

    def set_stores_list_ids(self) -> None:
        store_list = self.store_list()

        for store in store_list:
            self.stores_list_ids.append(store.cdsWithStock)

    def access_db(self) -> json:
        json_file = open('DB/dc.json', 'r')
        return json.load(json_file)

    def store_list(self) -> List[Stores]:
        json_db = self.access_db()

        store_list = list()
        try:
            for json_product in json_db:
                stores = namedtuple("Stores",  json_product.keys())(*json_product.values())
                #print("ProductId: ", stores.productId, "\nSkuId", stores.skuId, "\nEstoque Disponível: ", stores.availableStock, "\nListPrice: ", stores.listPrice, "\nSalePrice: ", stores.salePrice, "\nProductName: ", stores.productName, "\nLojas com Estoque: ", stores.cdsWithStock)
                logging.info(f" ProductId: {stores.productId}\n SkuId: {stores.skuId}\n Estoque Disponível: {stores.availableStock}\n listPrice: {stores.listPrice}\n SalePrice: {stores.salePrice}\n Nome do Produto: {stores.productName}\n Cidades com Estoque: {stores.cdsWithStock}\n")
                store_list.append(stores)
        except Exception as e:
            logging.error(f'{self.name} - Fail to get product list. Error={e}')
            self.get_server().disconnect()

        return store_list

    # def get_product_by_id(self, productId: str) -> Product:
    #
    #     try:
    #         store_list = self.store_list()
    #
    #         for product in store_list:
    #             if productId == product.productId:
    #                 return product
    #     except Exception as e:
    #         self.get_server().disconnect()

    def controll_messages(self, conn: socket, addr, response: str) -> bool:
        not_is_null = response != None and response != ''

        if not_is_null:
            logging.info(f'{self.name} - Receiving message: {response.strip()}')

            if 'list' in response:
                store_list = self.store_list()

                logging.info(f'{self.name} - Processing response: {response.strip()}, result is a store list.')

                logging.info(f'{self.name} -  send list all products: {(skuId for skuId in store_list)} to addr: {addr}')

                conn.send('Available Products:\n'.encode('utf-8'))
                for product in store_list:
                    message = f" ProductId: {stores.productId}\n SkuId: {stores.skuId}\n Estoque Disponível: {stores.availableStock}\n listPrice: {stores.listPrice}\n SalePrice: {stores.salePrice}\n Nome do Produto: {stores.productName}\n Cidades com Estoque: {stores.cdsWithStock}\n"
                    conn.send(message.encode('utf-8'))
            elif response in self.stores_list_ids:
                product = self.get_product_by_id(response)

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
                is_ok = self.controll_messages(conn, addr, resp)

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
