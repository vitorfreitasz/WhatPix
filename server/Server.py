from socket import *
import threading
from Connection import Connection

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.users = {}
        self.online_users = {}
        
    def start(self):

        self.socket.bind((self.host, self.port))
        self.socket.listen()
        print(f'Server running on: {self.host}:{self.port}')
        
    def connections(self):
        while True:
            conn, addr = self.socket.accept()
            self.thread_connection(conn, addr)
            
    def thread_connection(self, conn, addr):
        user = Connection(conn, addr, self)
        thread = threading.Thread(target=user.start)
        thread.start()