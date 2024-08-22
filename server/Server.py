from socket import *
import csv, os, time, threading, json

from Connection import Connection
from config.logger import logger

class Server:
    #   Constructor da classe do servidor.
    def __init__(self, host, port):
        self.host = host # Endereço IP do servidor
        self.port = port # Porta
        self.socket = socket(AF_INET, SOCK_STREAM) # Instancia do socket
        
        self.online_users = {} # Lista de usuários online
        self.userCounter = 1000000000000 # Contador de registros de usuário
        self.groupCounter = 2000000000000 # Contador de registros de grupos

        self.base_dir = os.path.dirname(__file__) # Diretório base da aplicação
        self.registeredUsers_path = os.path.join(self.base_dir, 'db', 'registeredUsers.csv') # Diretório do arquivo de armazenamento de registro de usuários
        self.awaitingMessages_path = os.path.join(self.base_dir, 'db', 'awaitingmessages.json') # Diretório do arquivo de armazenamento de mensagens pendentes
        self.groups_path = os.path.join(self.base_dir, 'db', 'groups.json') # Diretório do arquivo de armazenamento de grupos
        
    #   Método que inicia o servidor
    def start(self):
        logger.info("Iniciando o servidor.")
        self.socket.bind((self.host, self.port))
        if self.getRegisteredUSers():
            self.userCounter = int(self.getRegisteredUSers().pop())
            
        if self.getGroups():
            chave, _ = self.getGroups().popitem()
            self.groupCounter = int(chave)

        self.socket.listen()
        print(f'Server running on: {self.host}:{self.port}')
        logger.info(f"Server running on: {self.host}:{self.port}")
        self.connections()

    #   Retorna o Json com as mensagens pendentes
    def getAwaitingMessages(self): 
        with open(self.awaitingMessages_path, 'r') as file:
            return json.load(file)
        
    #   Remove as mensagens pendentes do usuário especificado, ou cria ele no armazenamento pela primeira vez
    def cleanupAwaitingMessagesForUser(self, user): 
        awaitingMessages = self.getAwaitingMessages()
        awaitingMessages[user] = []
        with open(self.awaitingMessages_path, 'w') as file:
            json.dump(awaitingMessages, file, indent=4)
            return

    #   Registra uma nova mensagem pendente para o usuário receber quando estiver online
    def registerAwaitingMessage(self, user, message): 
        awaitingMessages = self.getAwaitingMessages()
        awaitingMessages[user].append(message)   
        with open(self.awaitingMessages_path, 'w') as file:
            json.dump(awaitingMessages, file, indent=4)
            return

    #   Aguarda uma nova conexão chegar, ao chegar, cria uma nova thread para aquela conexão
    def connections(self): 
        while True:
            conn, addr = self.socket.accept()
            self.thread_connection(conn, addr)
            
    #   Registra um usuário, criando um novo identificador e retornado ao usuário
    def register(self, req, connectionClass):
        self.userCounter += 1
        codeUser = str(self.userCounter)

        self.online_users[codeUser] = connectionClass
        connectionClass.id = codeUser
        connectionClass.connection.sendall(f"02{codeUser}".encode('utf-8'))

        with open(self.registeredUsers_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([codeUser])

        self.cleanupAwaitingMessagesForUser(codeUser)

        logger.info(f"Novo usuário criado com o id: {codeUser}")
        return

    #   Retorna uma lista de usuários registrados
    def getRegisteredUSers(self): 
        try:
            with open(self.registeredUsers_path, 'r') as file:
                registeredUsersList = []
                reader = csv.reader(file)
                for row in reader:
                    if row:
                        registeredUsersList.append(row[0])
                return registeredUsersList

        except FileNotFoundError:
            print(f"Arquivo não encontrado.")

    #   Método para realizar Login, que verifica se há mensagens pendentes e as envia para ele, e envia também as confirmações para quem enviou.
    def login(self, req, connectionClass): 
        user_request = req[2:]

        if user_request in self.online_users: # verifica se o usuário já está online
            logger.warn(f"Usuário tentou logar com o id {user_request} mas já estava logado.")
            connectionClass.connection.sendall(f"00Usuário já esta online!".encode('utf-8'))
            return

        if not user_request in self.getRegisteredUSers(): # verifica se o usuário está registrado
            logger.warn(f"Tentativa de login com código não cadastrado. Código fornecido: {user_request}")
            connectionClass.connection.sendall(f"00Código identificador não cadastrado!".encode('utf-8'))
            return
        
        self.online_users[user_request] = connectionClass
        connectionClass.connection.sendall(f"04{user_request}".encode('utf-8'))
        connectionClass.id = user_request
        logger.info(f"Usuário {user_request} logado com sucesso.")

        messages = self.getAwaitingMessages()[user_request]
        if len(messages) > 0:
            for message in messages:
                newMessage = message.encode('utf-8')
                connectionClass.connection.sendall(newMessage)
                confirmSendMessage = f"07{message[15:28]}{str(time.time()).split('.')[0]}"
                if message[2:] == "06":
                    codeUser = message[2:15]
                    if codeUser in self.online_users:
                        connClass = self.online_users[codeUser]
                        connClass.connection.sendall(confirmSendMessage.encode('utf-8'))
                    else:
                        self.registerAwaitingMessage(codeUser, confirmSendMessage)
                time.sleep(1)
            self.cleanupAwaitingMessagesForUser(user_request)
        return

    #   Método que gerencia as mensagens enviadas pelos usuários, enviando para o destinatário e confirmando para quem enviou, ou armazenando a mensagem pendente.
    def message(self, req, connectionClass):
        user_send = req[2:15] # Id que enviou a mensagem
        user_receive = req[15:28] # Id que recebe
        timestemp = req[28:38] # Timestemp de envio
        message = req[38:] # Conteúdo da mensagem

        if user_receive[0] == "2":
            groups = self.getGroups()
            for memberId in groups[user_receive]:
                if memberId != user_send:    
                    if memberId in self.online_users:
                        self.online_users[memberId].connection.sendall(f"06{user_receive}{user_send}{timestemp}{message}".encode('utf-8'))
                    elif memberId in self.getRegisteredUSers():
                        self.registerAwaitingMessage(memberId, (f"06{user_receive}{user_send}{timestemp}{message}"))
                
        else:
            if user_receive in self.online_users:
                self.online_users[user_receive].connection.sendall(f"06{user_send}{user_receive}{timestemp}{message}".encode('utf-8'))
                connectionClass.connection.sendall(f"07{user_receive}{str(time.time()).split('.')[0]}".encode('utf-8'))
            elif user_receive in self.getRegisteredUSers():
                self.registerAwaitingMessage(user_receive, (f"06{user_send}{user_receive}{timestemp}{message}"))
        return
    
    #   Método que gerencia a confirmação de leitura.
    def confirmRead(self, req, connectionClass):
        user_send = req[2:15] # Id que enviou a mensagem
        user_receive = req[15:] # Id que recebe
        
        if user_send in self.online_users:
            self.online_users[user_send].connection.sendall(f"09{connectionClass.id}{user_receive}".encode('utf-8'))
        elif user_send in self.getRegisteredUSers():
            self.registerAwaitingMessage(user_send, (f"09{connectionClass.id}{user_receive}"))
        return
    
    def getGroups(self):
        with open(self.groups_path, 'r') as file:
            return json.load(file)
    
    def createGroup(self, req, connectionClass):
        creator = req[2:15] # Código do criador do grupo
        timestemp = req[15:25] # Timestemp de envio
        members = req[25:] # Código dos membros
        groups = self.getGroups()
        self.groupCounter += 1
        
        codeGroup = str(self.groupCounter)
        
        groups[codeGroup] = {}
        groups[codeGroup][creator]=[]
        memberscont = len(members) // 13
        init = 0
        final = 13
        for cont in range(memberscont):
            if members[init:final] not in self.getRegisteredUSers():
                connectionClass.connection.sendall(f"00Código de membro não cadastrado! ({members[init:final]})".encode('utf-8'))
                init += 13
                final += 13    
                continue
            if members[init:final] in self.online_users:
                self.online_users[members[init:final]].connection.sendall(f"11{codeGroup}{timestemp}{creator}{members}".encode('utf-8'))
                
            elif members[init:final] in self.getRegisteredUSers():
                self.registerAwaitingMessage(members[init:final], (f"11{codeGroup}{timestemp}{creator}{members}"))
            groups[codeGroup][members[init:final]] = []
            
            init += 13
            final += 13
            
        if creator in self.online_users:
            self.online_users[creator].connection.sendall(f"11{codeGroup}{timestemp}{creator}{members}".encode('utf-8'))
            
        elif creator in self.getRegisteredUSers():
            self.registerAwaitingMessage(creator, (f"11{codeGroup}{timestemp}{creator}{members}"))
        
        with open(self.groups_path, 'w') as file:
            json.dump(groups, file, indent=4)
            return
        
    #   Instacia uma classe para cada nova conexão, e cria uma thread para cada instancia da classe.
    def thread_connection(self, conn, addr):
        logger.info(f"Nova conexão: {conn}, {addr}")
        user = Connection(conn, addr, self)
        thread = threading.Thread(target=user.start)
        thread.start()
