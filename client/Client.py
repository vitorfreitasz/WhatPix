from socket import *
import time, threading
from zoneinfo import ZoneInfo
from datetime import datetime

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.codeUser = None
        self.lastMessageUser = 0

    def start(self): # se conecta com o servidor
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

    def close(self): # encerra a conexão com o servidor
        self.socket.close()
        
    def registerOrLogin(self): # pede para o usuário que se registre ou faça login
        while True:
            response = int(input('--------------------------------------\n\n Para cadastrar-se, digite 0.\n\n Para entrar digite 1.\n\n--------------------------------------\n\n'))

            if response == 0: # envia um código 01 para o servidor solicitando um novo cadastro 
                self.socket.send("01".encode('utf-8'))
                return
            elif response == 1: # pede para o usuário digitar seu número identificador
                while True:
                    id = str(input(f' Escreva o seu código identificador: '))
                    if len(id) == 13:
                        self.socket.send(f"03{id}".encode('utf-8')) # envia um código 03 e o id do usuário para o servidor solcitando login
                        return
                    else:
                        print("Erro: código identificador de tamanho irregular.")
        
    def awaitingComands(self): # espera por um comando do usuário para tomar uma ação
        while True:
            print("Lista de comandos:")
            print("/m -> Solicita o id do usuário que deseja enviar uma mensagem;")
            print("/r -> Envia mensagem para o usuário com o id da última mensagem recebida;")
            print("/cancelar -> Cancela o envio de mensagem;")
            print("/dc -> Desconecta do servidor;")
            print("/help -> Mostra a lista de todos os comandos;")
            print('\n Escreva seu comando: ')
            comand = input()
            self.handleComand(comand)
            
    def handleComand(self, comand): # verifica qual o comando o usuário digitou e toma uma ação com base nisso
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
            print("\n Desconectando do servidor...")
            time.sleep(2)
            self.socket.close()
            return
        if comand == '/help':
            self.awaitingComands()
        return
    
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
                thread = threading.Thread(target=self.awaitingComands)
                thread.start()
            if req[:2] == "04":
                self.codeUser = req[2:]
                print(f"\nUsuário logado!\n Id: ({self.codeUser})\n")
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
                