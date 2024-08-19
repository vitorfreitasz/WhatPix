from socket import *
import time, threading
from zoneinfo import ZoneInfo
from datetime import datetime

class Client:
    #   Constructor da classe do cliente.
    def __init__(self, host, port):
        self.host = host # Endereço do servidor
        self.port = port # Porta
        self.socket = socket(AF_INET, SOCK_STREAM) # Instancia da conexão com o servidor
        self.codeUser = None # Código identificador do usuário caso ele se registre ou logue.
        self.lastMessageUser = 0 # Código do último usuário a enviar mensagem para o cliente.

    # Inicia a conexão com o servidor, e cria a thread que gerencia as mensagens recebidas.
    def start(self): 
        self.socket.connect((self.host, self.port))
        print(f'\n\nConnected on: {self.host}:{self.port}')
        print("""
                   __,__
          .--.  .-\"     \"-.  .--.
         / .. \\/  .-. .-.  \\/ .. \\
        | |  '|  /   Y   \\  |'  | |
        | \\   \\  \\ 0 | 0 /  /   / |
         \\ '- ,\\.-\"\"\"\"\"\"\"-./, -' /
          ''-' /_   ^ ^   _\\ '-'
              |  \\._   _./  |
              \\   \\ '~' /   /
               '._ '-=-' _.'
                  '-----' 
        """)
        print(f'           Bem vindo ao WhatPix!')
        thread = threading.Thread(target=self.messages)
        thread.start()
        self.registerOrLogin()

    #   Encerra a conexão com o servidor
    def close(self): 
        self.socket.close()
        
    #   Método que solicita para o usuário que se registre ou faça login
    def registerOrLogin(self): 
        while True:
            response = int(input('--------------------------------------\n\n Para cadastrar-se, digite 0.\n\n Para entrar digite 1.\n\n--------------------------------------\n\n'))

            if response == 0: # Envia um código 01 para o servidor solicitando um novo cadastro 
                self.socket.send("01".encode('utf-8'))
                return
            elif response == 1: # Pede para o usuário digitar seu número identificador
                while True:
                    id = str(input(f' Escreva o seu código identificador: '))
                    if len(id) == 13:
                        self.socket.send(f"03{id}".encode('utf-8')) # Envia um código 03 e o id do usuário para o servidor solcitando login
                        return
                    else:
                        print("Erro: código identificador de tamanho irregular.")

    #   Espera por um comando do usuário para tomar uma ação.
    def awaitingComands(self): 
        while True:
            comand = input()
            self.handleComand(comand)

    #   Método que mostra todos os possíveis comandos.
    def printComandsList(self):
        print("\nLista de comandos:")
        print("/m -> Solicita o id do usuário que deseja enviar uma mensagem;")
        print("/r -> Envia mensagem para o usuário com o id da última mensagem recebida;")
        print("/cancelar -> Cancela o envio de mensagem;")
        print("/dc -> Desconecta do servidor;")
        print("/help -> Mostra a lista de todos os comandos;\n\n")
        
    #   Verifica qual o comando o usuário digitou e toma uma ação com base nisso.
    def handleComand(self, comand): 
        if comand == '/m':
            while True:
                dest = str(input(f"Para quem deseja enviar (digite '/cancelar' para cancelar): "))
                if dest == '/cancelar':
                    return
                if len(dest) == 13:
                    message = str(input(f"Mensagem: "))
                    if len(message) <= 218:
                        finalMessage = f"05{self.codeUser}{dest}{str(time.time()).split('.')[0]}{message}".encode('utf-8')
                        
                        self.socket.send(finalMessage)
                        return
        if comand == '/r':
            if self.lastMessageUser != 0:
                while True:
                    message = str(input(f"Respondendo para ({self.lastMessageUser}).\n Mensagem (digite /cancelar para cancelar): "))
                    if message == '/cancelar':
                        return
                    if len(message) <= 218:
                        finalMessage = f"05{self.codeUser}{self.lastMessageUser}{str(time.time()).split('.')[0]}{message}".encode('utf-8')
                        
                        self.socket.send(finalMessage)
                        return
            else:
                print("Não há ninguém para responder.")
        if comand == '/dc':
            print("\n Desconectando do servidor...\n\n")
            time.sleep(2)
            self.socket.close()
            return
        if comand == '/help':
            self.printComandsList()
        return
    
    #   Gerencia o recebimento de mensagens, e com base no código recebido, realiza a ação designada.
    def messages(self):
        while True:
            data = self.socket.recv(256)
            req = data.decode()
            if req[:2] == '00':
                print(f"{req[2:]}\n")
                self.registerOrLogin()
            if req[:2] == "02":
                self.codeUser = req[2:]
                print(f"\nUsuário cadastrado!\n Id: ({self.codeUser})\n")
                self.printComandsList()
                print('\n Escreva seu comando: ')
                thread = threading.Thread(target=self.awaitingComands)
                thread.start()
            if req[:2] == "04":
                self.codeUser = req[2:]
                print(f"\nUsuário logado!\n Id: ({self.codeUser})\n")
                self.printComandsList()
                print('\n Escreva seu comando: ')
                thread = threading.Thread(target=self.awaitingComands)
                thread.start()
            if req[:2] == '06':
                print(f"\nMensagem de ({req[2:15]}): {req[38:]}\n")
                self.lastMessageUser = req[2:15]
                self.socket.send(f"08{req[2:15]}{str(time.time()).split('.')[0]}".encode('utf-8'))
            if req[:2] == '07':
                print(f"\nEntregue para ({req[2:15]}). ({datetime.fromtimestamp(int(req[15:25]), tz=ZoneInfo('America/Sao_Paulo'))}).\n")
            if req[:2] == '09':
                print(f"\nVisualizada por ({req[2:15]}) as ({datetime.fromtimestamp(int(req[15:25]), tz=ZoneInfo('America/Sao_Paulo'))}) .\n")
                