from config.logger import logger
import threading

class Connection:
    def __init__(self, conn, addr, server):
        super().__init__()
        self.connection = conn
        self.address = addr
        self.server = server
        self.online = True
        self.number = None
        
    def awaitingResponse(self):
        while True:
            data = self.connection.recv(1024)
            if not data:
                break
            req = data.decode()
            print('oiiiiii')
            self.server.handleResponse(req)

        
    def start(self):
        logger.info(f"Nova conexão criada com o endereço: {self.address}")
        self.connection.sendall(b"Bem vindo ao WhatPix!")
        thread = threading.Thread(target=self.awaitingResponse)
        thread.start()
        
        
        
