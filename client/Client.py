from socket import *

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)

    def start(self): # se conecta com o servidor
        self.socket.connect((self.host, self.port))
        print(f'Connected on: {self.host}:{self.port}')
        print("\n\nConnected!!!\n\n")
        self.messages()

    def close(self): # encerra a conexão com o servidor
        self.socket.close()

    def messages(self):
        while True:
            data = self.socket.recv(1024)
            print(f"{data}")
