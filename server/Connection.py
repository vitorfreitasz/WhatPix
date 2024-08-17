import threading

from config.logger import logger

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
        try:
            while True:
                data = self.connection.recv(256)
                if not data:
                    break
                req = data.decode()
                if req:
                    self.handleResponse(req)
        except (ConnectionResetError, BrokenPipeError) as e:
            print(f"Conexão perdida com ({self.id}).")
        finally:
            self.cleanup()
            
    def cleanup(self):
        self.online = False
        del self.server.online_users[self.id]
        if self.connection:
            self.connection.close()
        print(f"Conexão fechada com ({self.id}).")
        return
        
    def handleResponse(self, req):
        action = req[:2]
        
        if action == '01':
            self.server.register(req, self)
            return
        elif action == '03':
            self.server.login(req, self)
            return
        elif action == '05':
            self.server.message(req, self)
            return
        elif action == '08':
            self.server.confirmRead(req, self)
            return
        
        else:
            self.connection.sendall(b"0000000000000")
            return
            
    def start(self):
        logger.info(f"Nova conexão criada com o endereço: {self.address}")
        self.connection.sendall(b" Bem vindo ao WhatPix!\n\n")
        thread = threading.Thread(target=self.awaitingResponse)
        thread.start()
        