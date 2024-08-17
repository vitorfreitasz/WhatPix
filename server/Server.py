from socket import *
import csv, os, time, threading

from Connection import Connection
from config.logger import logger

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.online_users = {}
        self.awaiting_messages = {}
        self.userCounter = 1000000000000

        self.base_dir = os.path.dirname(__file__) # diretório base do app
        self.registeredUsers_path = os.path.join(self.base_dir, 'db', 'registeredUsers.csv')
        
    def start(self): # inicia o servidor
        logger.info("Iniciando o servidor.")
        self.socket.bind((self.host, self.port))
        
        if self.getRegisteredUSers():
            self.userCounter = int(self.getRegisteredUSers().pop())

        self.socket.listen()
        print(f'Server running on: {self.host}:{self.port}')
        logger.info(f"Server running on: {self.host}:{self.port}")
        self.connections()
        
    def connections(self): # cria uma nova thread para cada solicitação de conexão
        while True:
            conn, addr = self.socket.accept()
            self.thread_connection(conn, addr)
            #print(self.online_users)
            
    def register(self, req, connectionClass):
        self.userCounter += 1
        codeUser = str(self.userCounter)

        self.online_users[codeUser] = connectionClass
        self.awaiting_messages[codeUser] = []
        connectionClass.id = codeUser
        connectionClass.connection.sendall(f"02{codeUser}".encode('utf-8'))

        with open(self.registeredUsers_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([codeUser])

        logger.info(f"Novo usuário criado com o id: {codeUser}")
        return

    def getRegisteredUSers(self): # retorna uma lista de usuários registrados
        try:
            with open(self.registeredUsers_path, 'r') as file:
                registeredUsersList = []
                reader = csv.reader(file)
                for row in reader:
                    if row:
                        registeredUsersList.append(row[0])
                return registeredUsersList

        except FileNotFoundError:
            print(f"Arquivo não encontrado.")

    def login(self, req, connectionClass): # método para realizar login
        if req[2:] in self.online_users: # verifica se o usuário já está online
            logger.warn(f"Usuário tentou logar com o id {req[2:]} mas já estava logado.")
            connectionClass.connection.sendall(f"00Usuário já esta online!".encode('utf-8'))
            return

        if req[2:] in self.getRegisteredUSers(): # verifica se o usuário está registrado
            self.online_users[req[2:]] = connectionClass
            
            connectionClass.connection.sendall(f"04{req[2:]}".encode('utf-8'))
            connectionClass.id = req[2:]
            messages = self.awaiting_messages[req[2:]]
            if len(messages) > 0:
                for message in messages:
                    newMessage = message
                    connectionClass.connection.sendall(newMessage)
                    confirmSendMessage = f"07{message.decode()[15:28]}{str(time.time()).split('.')[0]}"
                    if message.decode()[2:] == "06":
                        codeUser = message.decode()[2:15]
                        if codeUser in self.online_users:
                            connClass = self.online_users[codeUser]
                            connClass.connection.sendall(confirmSendMessage.encode('utf-8'))
                        else:
                            self.awaiting_messages[codeUser].append(confirmSendMessage.encode('utf-8'))
                    time.sleep(1)
                self.awaiting_messages[req[2:]] = []
        else:
            logger.warn(f"Tentativa de login com código não cadastrado. Código fornecido: {req[2:]}")
            connectionClass.connection.sendall(f"00Código identificador não cadastrado!".encode('utf-8'))
        return
    
    def message(self, req, connectionClass):
        if req[15:28] in self.online_users:
            self.online_users[req[15:28]].connection.sendall(f"06{req[2:15]}{req[15:28]}{req[28:38]}{req[38:]}".encode('utf-8'))
            connectionClass.connection.sendall(f"07{req[15:28]}{str(time.time()).split('.')[0]}".encode('utf-8'))
        elif req[15:28] in self.getRegisteredUSers():
            self.awaiting_messages[req[15:28]].append(f"06{req[2:15]}{req[15:28]}{req[28:38]}{req[38:]}".encode('utf-8'))
        return
    
    def confirmRead(self, req, connectionClass):
        
        if req[2:15] in self.online_users:
            self.online_users[req[2:15]].connection.sendall(f"09{connectionClass.id}{req[15:]}".encode('utf-8'))
        elif req[2:15] in self.getRegisteredUSers():
            self.awaiting_messages[req[2:15]].append(f"09{connectionClass.id}{req[15:]}".encode('utf-8'))
        return
        
    def thread_connection(self, conn, addr):
        logger.info(f"Nova conexão: {conn}, {addr}")
        user = Connection(conn, addr, self)
        thread = threading.Thread(target=user.start)
        thread.start()
    