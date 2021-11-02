import logging, socket

class Server():
    message: dict
    port: int
    name: str
    ip: str

    def __init__(self, port: int, name: str, ip: str):
        self.port = port
        self.name = name
        self.ip = ip
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def start_socket(self):
        logging.info(f"{self.name} - Start server in host={self.ip} porta={self.port}.")

        self.server.bind((self.ip, self.port))

        
    def disconnect(self):
        self.server.close()
