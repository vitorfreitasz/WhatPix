from socket import *
import threading
from Connection import Connection

from config.logger import logger

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.createduser=1000000000000
        self.users = {}
        self.online_users = {}
        self.awaiting_messages = {}
        
    def start(self): # inicia o servidor
        logger.info("Iniciando o servidor.")
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        print(f'Server running on: {self.host}:{self.port}')
        self.connections()
        
    def connections(self): # cria uma nova thread para cada solicitação de conexão
        while True:
            conn, addr = self.socket.accept()
            self.thread_connection(conn, addr)
            print(self.online_users)
            
    def register(self, req, connectionClass):
        codeUser = str(self.createduser)
        self.createduser+=1
        self.users[codeUser] = connectionClass
        self.online_users[codeUser] = connectionClass
        self.awaiting_messages[codeUser] = []
        connectionClass.id = codeUser
        connectionClass.connection.sendall(f"02{codeUser}".encode('utf-8'))
        return
        
    def login(self, req, connectionClass):
        if req[2:] in self.users:
            self.users[req[2:]] = connectionClass
            self.online_users[req[2:]] = connectionClass
            
            connectionClass.connection.sendall(f"04{req[2:]}".encode('utf-8'))
            connectionClass.id = req[2:]
            messages = self.awaiting_messages[req[2:]]
            for message in messages:
                newMessage = message
                confirmSendMessage = '07' + f'{message[15:28],message[28:38]}'
                connectionClass.connection.sendall(newMessage.encode('utf-8'))
                codeUser = message[2:16]
                if codeUser in self.online_users:
                    conn = self.online_users[codeUser]
                    conn.sendall(confirmSendMessage.encode('utf-8'))
                else:
                    self.awaiting_messages[codeUser].append(message)
            self.awaiting_messages[req[2:]] = []
        else:
            connectionClass.connection.sendall(f"00Código identificador não cadastrado!".encode('utf-8'))
        return
    
    def message(self, conn, addr, req):
        print(conn)
        print(req[15:28])
        if req[15:28] in self.online_users:
            self.online_users[req[15:28]].connection.sendall(f"06{req[2:15],req[15:28],req[28:38],req[38:]}".encode('utf-8'))
        elif req[15:28] in self.users:
            self.awaiting_messages[req[15:28]].append(f"06{req[2:15],req[15:28],req[28:38],req[38:]}".encode('utf-8'))
        return
        
    def thread_connection(self, conn, addr):
        user = Connection(conn, addr, self)
        thread = threading.Thread(target=user.start)
        thread.start()
    
