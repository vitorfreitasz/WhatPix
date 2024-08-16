from socket import *
import time
from time import sleep
import threading
from zoneinfo import ZoneInfo
from datetime import datetime

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.codeUser = None

    def start(self): # se conecta com o servidor
        self.socket.connect((self.host, self.port))
        print(f'Connected on: {self.host}:{self.port}')
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

        thread = threading.Thread(target=self.messages)
        thread.start()
        self.registerOrLogin()

    def close(self): # encerra a conexão com o servidor
        self.socket.close()
        
    def registerOrLogin(self):
        while True:
            response = int(input('--------------------------------------\n\n Para cadastrar-se, digite 0.\n\n Para entrar digite 1.\n\n--------------------------------------\n\n'))

            if response == 0:
                self.socket.send("01".encode('utf-8'))
                return
            elif response == 1:
                while True:
                    id = str(input(f' Escreva o seu código identificador: '))
                    if len(id) == 13:
                        self.socket.send(f"03{id}".encode('utf-8'))
                        return
                    else:
                        print("Erro: código identificador de tamanho irregular.")
        
    def awaitingComands(self):
        while True:
            comand = input('Escreva seu comando: ')
            self.handleComand(comand)
            return
            
    def handleComand(self, comand):
        if comand == 0:
            while True:
                dest = str(input(f"Para quem deseja enviar (digite 'cancelar' para cancelar): "))
                if dest == 'cancelar':
                    break
                if len(dest) == 13:
                    message = str(input(f"Mensagem: "))
                    if len(message) <= 218:
                        finalMessage = f"05{self.codeUser}{dest}{str(time.time()).split('.')[0]}{message}".encode('utf-8')
                        self.socket.send(f"{finalMessage}".encode('utf-8'))
                        break
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
                print(f"Usuário cadastrado!\n Id: ({self.codeUser})")
                thread = threading.Thread(target=self.awaitingComands)
                thread.start()
            if req[:2] == "04":
                self.codeUser = req[2:]
                print(f"Usuário logado!\n Id: ({self.codeUser})")
                thread = threading.Thread(target=self.awaitingComands)
                thread.start()
            if req[:2] == '06':
                print(f"Mensagem de ({req[2:15]}): {req[38:]}")
            if req[:2] == '07':
                print(f"Mensagem entregue as ({datetime.fromtimestamp(int(req[15:]), tz=ZoneInfo('America/Sao_Paulo'))}) para ({req[2:15]}).")