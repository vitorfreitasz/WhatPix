import threading

from config.logger import logger

class Connection:
    #   Constructor da classe de conexão.
    def __init__(self, conn, addr, server):
        super().__init__()
        self.connection = conn # Conexão
        self.address = addr # Endereço
        self.server = server # Instancia da classe do servidor
        self.online = False # Usuário online ou não.
        self.id = None # Identificador do usuário, caso esteja cadastrado ou logado
        
    #   Método que aguarda mensagens vindas do servidor.
    def awaitingResponse(self):
        try:
            while True:
                data = self.connection.recv(256)
                if not data:
                    break
                req = data.decode()
                if req:
                    self.handleResponse(req)
        except (ConnectionResetError, BrokenPipeError) as e:
            logger.warn(f"Conexão perdida com ({self.id}).")
            #print(f"Conexão perdida com ({self.id}).")
        finally:
            self.cleanup()
        
    #   Método que fecha a conexão com o cliente, excluindo-o dos usuários online e encerrando a conexão
    def cleanup(self):
        self.online = False
        del self.server.online_users[self.id]
        if self.connection:
            self.connection.close()
        logger.info(f"Conexão fechada com ({self.id}).")
        #print(f"Conexão fechada com ({self.id}).")
        return
        
    #   Método que recebe a requisição, e gerencia com base no código enviado
    def handleResponse(self, req): 
        action = req[:2]
        
        if action == '01': # Se 01, então registra um novo usuário
            self.server.register(req, self)
            return
        elif action == '03': # Se 03, então realiza o login do usuário
            self.server.login(req, self)
            return
        elif action == '05': # Se 05, então gerencia a mensagem enviando e confirmando envio, ou armazenando.
            self.server.message(req, self)
            return
        elif action == '08': # Se 08, então gerencia a confirmação de leitura da mensagem.
            self.server.confirmRead(req, self)
            return
        elif action == '10': # Se 10, então gerencia a criação de um grupo.
            self.server.createGroup(req, self)
            return
        
        else: # Se nenhuma das opções, retorna 00 (erro)
            self.connection.sendall(f"00Erro: código de protocolo não identificado.".encode('utf-8'))
            return
            
    #   Método que inicia a conexão, criando uma thread para o aguardo de mensagens.
    def start(self):
        logger.info(f"Nova conexão criada com o endereço: {self.address}")
        self.connection.sendall(b" Bem vindo ao WhatPix!\n\n")
        thread = threading.Thread(target=self.awaitingResponse)
        thread.start()
        