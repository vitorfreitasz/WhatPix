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
        response = input(f'--------------------------------------\n\nPara cadastrar-se, digite 0.\n\n Para entrar digite 1.\n\n--------------------------------------\n\n')
        if response == 0:
            self.socket.send('Hello world 1')
        elif response == 1:
            self.socket.send('Hello world 1')
        
    def messages(self):
        while True:
            data = self.socket.recv(1024)
            print(f"{data}")
