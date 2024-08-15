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
        print('Criou thread pelo menos.')
        while True:
            data = self.connection.recv(1024)
            req = data.decode()
            if req:
                print('RECEBI')
            self.server.handleResponse(req)
            if req == "Hello world 0":
                self.connection.sendall(b"XYZ")

        
    def start(self):
        logger.info(f"Nova conexão criada com o endereço: {self.address}")
        self.connection.sendall(b"Bem vindo ao WhatPix!")
        thread = threading.Thread(target=self.awaitingResponse)
        thread.start()
        
        
        
