import logging, time
from .client import Client
from .server import Server

TIMEOUT = 2
MAX_EXECUTION = 10

class Machine():
    client: Client
    server: Server
    name: str
    slave_port: int
    
    def __init__(self, name, port, slave_port, ip):
        self.name = name
        self.server = Server(port, name, ip)
        self.client = Client(ip)
        self.slave_port = slave_port

    def get_server(self) -> Server:
        return self.server

    def get_client(self) -> Client:
        return self.client

    def execute_machine(self):
        pass
