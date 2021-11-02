import socket

class Client():
    ip: str

    def __init__(self, ip: str):
        self.ip = ip
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def init_client_socket(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_message(self, message, port_destination):
        try:
            self.client.connect((self.ip, port_destination))
            self.client.send(message.encode('utf-8'))
        except Exception:
            self.client.send(message.encode('utf-8'))
