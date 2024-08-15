from socket import *
from time import sleep
import threading

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)

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
        sleep(2)
        while True:
            response = int(input(f'--------------------------------------\n\n Para cadastrar-se, digite 0.\n\n Para entrar digite 1.\n\n--------------------------------------\n\n '))
            print('Decisão tomada.')
            if response == 0:
                print('Enviando mensagem...')
                self.socket.send(b"Hello world 0")
                print('Mensagem enviada.')
            elif response == 1:
                print('Enviando mensagem...')
                self.socket.send(b"Hello world 1")
                print('Mensagem enviada.')
        return
        
    def messages(self):
        while True:
            data = self.socket.recv(1024)
            print(f"{data.decode()}")
            if data.decode() == "XYZ":
                print(f'\n\n Código XYZ retornado do Hello world 0.\n\n')