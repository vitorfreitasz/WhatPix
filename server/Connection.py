from config.logger import logger
import threading
from time import sleep

class Connection:
    def __init__(self, conn, addr, server):
        super().__init__()
        self.connection = conn
        self.address = addr
        self.server = server
        self.online = True
        self.id = None
        
    def awaitingResponse(self):
        #logger.info('Criou nova thread.')
        while True:
            try:
                data = self.connection.recv(256)
                if not data:
                    break
                req = data.decode()
                if req:
                    self.handleResponse(req)
            except:
                del self.server.online_users[self.id]
                self.connection.close()
        
    def handleResponse(self, req):
        action = req[:2]
        
        if action == '01':
            self.server.register(req, self)
        elif action == '03':
            self.server.login(req, self)
        elif action == '05':
            self.server.message(req, self)
        elif action == '08':
            self.confirmaleitura
        
        else:
            self.connection.sendall(b"0000000000000")
            
    def start(self):
        logger.info(f"Nova conexão criada com o endereço: {self.address}")
        self.connection.sendall(b" Bem vindo ao WhatPix!\n\n")
        thread = threading.Thread(target=self.awaitingResponse)
        thread.start()
        