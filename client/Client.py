import csv
import os
from socket import *
import time, threading, json
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
        self.lastGroupAdded = None # Código do último grupo a ser adicionado.
        self.inChat = False # Boleano para verificar se a pessoa está no chat com outra.
        self.base_dir = os.path.dirname(__file__) # Diretório base da aplicação
        self.contacts_path = os.path.join(self.base_dir, 'db', 'contacts.json') # Diretório para o arquivo json que armazena os contatos e o histórico de mensagens.

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
        
    #   Pega do arquivo, o Json dos contatos.
    def getContacts(self): 
        with open(self.contacts_path, 'r') as file:
            return json.load(file)
        
    #   Método que registra um novo contato.
    def registerContact(self, user, name):
        contact = f"{user}-{name}"
        contactsArray = self.getContacts()
        if self.codeUser in contactsArray:
            contactsArray[self.codeUser]["contacts"].append(contact)
            with open(self.contacts_path, 'w') as file:
                json.dump(contactsArray, file, indent=4)
            return
        else:
            contactsArray[self.codeUser] = {}
            contactsArray[self.codeUser]["contacts"] = []
            contactsArray[self.codeUser]["messages"] = []
            
            contactsArray[self.codeUser]["contacts"].append(contact)
            with open(self.contacts_path, 'w') as file:
                json.dump(contactsArray, file, indent=4)
            return

    #   Método que pega os contatos registrados.
    def getRegisteredContact(self): 
        contactsArray = self.getContacts()
        
        if self.codeUser in contactsArray:
            contacts_list = contactsArray[self.codeUser]["contacts"]
            return contacts_list
        return []
                
        
    #   Método que salva mensagens no histórico de mensagens.
    def registerMessageContact(self, message):
        
        contactsArray = self.getContacts()
        
        if self.codeUser in contactsArray:
            contactsArray[self.codeUser]["messages"].append(message)   
            with open(self.contacts_path, 'w') as file:
                json.dump(contactsArray, file, indent=4)
                return
        else:
            contactsArray[self.codeUser] = {}
            contactsArray[self.codeUser]["contacts"] = []
            contactsArray[self.codeUser]["messages"] = []
            contactsArray[self.codeUser]["messages"].append(message)   
            with open(self.contacts_path, 'w') as file:
                json.dump(contactsArray, file, indent=4)
                return
                
    #   Método que pega o histórico de mensagens de uma conversa específica.
    def getMessagesSpecific(self, user): 
        contactsArray = self.getContacts()
        historyMessages = []
        if self.codeUser in contactsArray:
            for mensage in contactsArray[self.codeUser]["messages"]:
                if mensage[2:15] == user or mensage[15:28] == user:
                    historyMessages.append(mensage)
        return historyMessages
        
    
        
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
            comand = input(" ")
            self.handleComand(comand)

    #   Método que mostra todos os possíveis comandos.
    def printComandsList(self):
        print("\n Lista de comandos:")
        print(" /m -> Solicita o id do usuário que deseja enviar uma mensagem;\n /r -> Envia mensagem para o usuário com o id da última mensagem recebida;\n /cancelar -> Cancela o envio de mensagem;\n /dc -> Desconecta do servidor;\n /rc -> Registra um novo contato.\n /cl -> Lista os contatos.\n /cm -> Envia mensagem para o contato que escolher.\n /cg -> Cria um grupo.\n /help -> Mostra a lista de todos os comandos;\n\n")
        
    #   Verifica qual o comando o usuário digitou e toma uma ação com base nisso.
    def handleComand(self, comand): 
        
        #    Solicita o id do usuário que deseja enviar uma mensagem
        if comand == '/m': 
            while True:
                dest = str(input(f"\n Para quem deseja enviar (digite '/cancelar' para cancelar): "))
                if dest == '/cancelar':
                    return
                if len(dest) == 13:
                    message = str(input(f"\n Mensagem: "))
                    if len(message) <= 218:
                        finalMessage = f"05{self.codeUser}{dest}{str(time.time()).split('.')[0]}{message}".encode('utf-8')
                        
                        self.registerMessageContact(finalMessage.decode())
                        self.socket.send(finalMessage)
                        return
                    
        #    Envia mensagem para o usuário com o ID da última mensagem recebida
        elif comand == '/r': 
            if self.lastMessageUser != 0:
                while True:
                    message = str(input(f" Respondendo para ({self.lastMessageUser}).\n Mensagem (digite /cancelar para cancelar): "))
                    if message == '/cancelar':
                        return
                    if len(message) <= 218:
                        finalMessage = f"05{self.codeUser}{self.lastMessageUser}{str(time.time()).split('.')[0]}{message}".encode('utf-8')
                        
                        self.registerMessageContact(finalMessage.decode())
                        self.socket.send(finalMessage)
                        return
            else:
                print("Não há ninguém para responder.")
                return
            
        #   Registra um novo contato.
        elif comand == '/rc':
            print("\n Registrando contato (digite /cancelar para cancelar)\n")
            while True:
                contact = str(input(f" Cód. Identificador: "))
                if contact == '/cancelar':
                    return
                if len(contact) == 13:
                    name = str(input(f" Digite o nome do contato: "))
                    if name == '/cancelar':
                        return
                    self.registerContact(contact, name)
                    print(f"\n Contato salvo!\n")
                    return
        
        #   Lista todos os contatos.
        elif comand == '/cl':
            contact_list = self.getRegisteredContact()
            if contact_list:
                print("\n Lista de contatos:\n")
                for ctt in contact_list:
                    contact = ctt.split('-')
                    print(f" {contact[1]} -> {contact[0]}\n")
            else: 
                print("\n Nenhum contato salvo.\n")
            return
        
        #   Envia mensagem para o contato que escolher.
        elif comand == '/cm':
            print("--------------------------------------------------------------------------------------------------------------")
            print("\n Para enviar uma mensagem para algum contato, digite o nome de quem deseja enviar (Digite /sair para sair): \n")
            contact_list = self.getRegisteredContact()
            if contact_list:
                for ctt in contact_list:
                    contact = ctt.split('-')
                    print(f" {contact[1]} -> {contact[0]}\n")
                print("--------------------------------------------------------------------------------------------------------------")
                while True:
                    name = str(input(f" Nome do contato: "))
                    if name == "/sair":
                        return
                    for ctt in contact_list:
                        contact = ctt.split('-')
                        if contact[1] == name:
                            for msg in self.getMessagesSpecific(contact[0]):
                                if msg[:2] == "06":
                                    print(f"\n\n ({str(datetime.fromtimestamp(int(msg[28:38]), tz=ZoneInfo('America/Sao_Paulo')))[11:16]}) {contact[1]}: {msg[38:]}\n\n")
                                    
                                elif msg[:2] == "05":
                                    print(f"\n\n ({str(datetime.fromtimestamp(int(msg[28:38]), tz=ZoneInfo('America/Sao_Paulo')))[11:16]}) Você: {msg[38:]}\n\n")
                                    
                            while True:
                                message = str(input(f" Mensagem: "))
                                if message == "/sair":
                                    return
                                if len(message) <= 218:
                                    finalMessage = f"05{self.codeUser}{contact[0]}{str(time.time()).split('.')[0]}{message}".encode('utf-8')
                                
                                    self.registerMessageContact(finalMessage.decode())
                                    self.socket.send(finalMessage)
                                    print(f"\n")
                                    return
                                else:
                                    print("\n Mensagem muito grande. Máx 218 caractéres.\n")
                    print(f"\n Nenhum contato encontrado com este nome.\n")
            else: 
                print("\n Nenhum contato salvo.\n")
                time.sleep(1)
                print("\n Operação cancelada.\n")
            return
                
        #   Cria um grupo.
        elif comand == '/cg':
            print(f"\n Criação de grupo (digite /cancelar para cancelar, ou /parar para parar)\n")
            usersCodes = ""
            cont = 0
            while cont < 7:
                print(f"Pediu {cont} ids")
                id = str(input(f"\n Digite um código de usuário: "))
                if id == "/cancelar":
                    return
                if id == "/parar":
                    break
                if len(id) == 13:
                    usersCodes+=id
                    cont+=1
                    print(f"\n Usuário adicionado!\n")
            
            if len(usersCodes) < 13:
                print(f"\n Erro: é necessário adicionar ao menos uma pessoa no grupo.\n")
                return
            
            finalMessage = f"10{self.codeUser}{str(time.time()).split('.')[0]}{usersCodes}"
                    
            self.registerMessageContact(finalMessage)
            self.socket.send(finalMessage.encode('utf-8'))
            return
        
        #   Comando para adicionar um grupo recém criado aos contatos
        elif comand == '/sim':
            print("\n Registrando grupo aos contatos (digite /cancelar para cancelar)\n")
            while True:
                name = str(input(f" Digite o nome do contato: "))
                if name == '/cancelar':
                    return
                self.registerContact(self.lastGroupAdded, name)
                print(f"\n Contato salvo!\n")
                return
                
        #   Desconecta do servidor
        elif comand == '/dc':
            print("\n Desconectando do servidor...\n\n")
            time.sleep(2)
            self.socket.close()
            return
        
        #   Lista todos os comandos.
        elif comand == '/help':
            self.printComandsList()
            return
        else:
            print("\n Comando não reconhecido.\n")
        return
    
    #   Gerencia o recebimento de mensagens, e com base no código recebido, realiza a ação designada.
    def messages(self):
        while True:
            data = self.socket.recv(256)
            req = data.decode()
            #   Código 00: Determinado para casos de erros.
            if req[:2] == '00':
                print(f"\n ERRO: \n {req[2:]}\n")
                if not self.codeUser:
                    self.registerOrLogin()
                
            
            #   Código 02: Determinado para retorno de uma tentativa de cadastro.
            if req[:2] == "02":
                self.codeUser = req[2:]
                print(f"\n Usuário cadastrado!\n Id: ({self.codeUser})\n")
                self.printComandsList()
                print('\n Escreva seu comando: ')
                thread = threading.Thread(target=self.awaitingComands)
                thread.start()
                
            
            #   Código 04: Determinado para retorno de tentativa de login.
            if req[:2] == "04":
                self.codeUser = req[2:]
                print(f"\n Usuário logado!\n Id: ({self.codeUser})\n")
                self.printComandsList()
                print('\n Escreva seu comando: ')
                thread = threading.Thread(target=self.awaitingComands)
                thread.start()
                
            
            #   Código 06: Determinado para tratamento de recebimento de mensagens.
            if req[:2] == '06':
                contactOrNot = "None"
                for contact in self.getRegisteredContact():
                    if contact.split('-')[0] == req[2:15]:
                        contactOrNot = contact.split('-')[1]
                if contactOrNot == 'None':
                    if req[2] == "2":
                        contactOrNotUserSend = "None"
                        for contact in self.getRegisteredContact():
                            if contact.split('-')[0] == req[15:28]:
                                contactOrNotUserSend = contact.split('-')[1]
                        if contactOrNotUserSend == 'None':
                            print(f"\n\n ({str(datetime.fromtimestamp(int(req[28:38]), tz=ZoneInfo('America/Sao_Paulo')))[11:16]}) (Grupo - {req[2:15]}) {req[15:28]}: {req[38:]}\n\n")
                        else:
                            print(f"\n\n ({str(datetime.fromtimestamp(int(req[28:38]), tz=ZoneInfo('America/Sao_Paulo')))[11:16]}) (Grupo - {req[2:15]}) {contactOrNotUserSend}: {req[38:]}\n\n")
                    else:
                        print(f"\n\n ({str(datetime.fromtimestamp(int(req[28:38]), tz=ZoneInfo('America/Sao_Paulo')))[11:16]}) Usuário - {req[2:15]}: {req[38:]}\n\n")
                else:
                    if req[2] == "2":
                        contactOrNotUserSend = "None"
                        for contact in self.getRegisteredContact():
                            if contact.split('-')[0] == req[15:28]:
                                contactOrNotUserSend = contact.split('-')[1]
                        if contactOrNotUserSend == 'None':
                            print(f"\n\n ({str(datetime.fromtimestamp(int(req[28:38]), tz=ZoneInfo('America/Sao_Paulo')))[11:16]}) ({contactOrNot}) {req[15:28]}: {req[38:]}\n\n")
                        else:
                            print(f"\n\n ({str(datetime.fromtimestamp(int(req[28:38]), tz=ZoneInfo('America/Sao_Paulo')))[11:16]}) ({contactOrNot}) {contactOrNotUserSend}: {req[38:]}\n\n")
                    else:
                        print(f"\n\n ({str(datetime.fromtimestamp(int(req[28:38]), tz=ZoneInfo('America/Sao_Paulo')))[11:16]}) {contactOrNot}: {req[38:]}\n\n")
                self.lastMessageUser = req[2:15]
                self.registerMessageContact(req)
                self.socket.send(f"08{req[2:15]}{str(time.time()).split('.')[0]}".encode('utf-8'))
                
            
            #   Código 07: Determinado para retorno de confirmação de entrega de mensagens.
            if req[:2] == '07':
                contactOrNot = "None"
                for contact in self.getRegisteredContact():
                    if contact.split('-')[0] == req[2:15]:
                        contactOrNot = contact.split('-')[1]
                if contactOrNot == 'None':
                    print(f"\n ({str(datetime.fromtimestamp(int(req[15:25]), tz=ZoneInfo('America/Sao_Paulo')))[11:16]}) Entregue para {req[2:15]}.")
                else:
                    print(f"\n ({str(datetime.fromtimestamp(int(req[15:25]), tz=ZoneInfo('America/Sao_Paulo')))[11:16]}) Entregue para {contactOrNot}.")
            
            
            #   Código 09: Determinado para confirmação de leitura de mensagens.
            if req[:2] == '09':
                contactOrNot = "None"
                for contact in self.getRegisteredContact():
                    if contact.split('-')[0] == req[2:15]:
                        contactOrNot = contact.split('-')[1]
                if contactOrNot == 'None':
                    print(f"\n ({str(datetime.fromtimestamp(int(req[15:25]), tz=ZoneInfo('America/Sao_Paulo')))[11:16]}) Visualizada por {req[2:15]}.\n")
                else:
                    print(f"\n ({str(datetime.fromtimestamp(int(req[15:25]), tz=ZoneInfo('America/Sao_Paulo')))[11:16]}) Visualizada por {contactOrNot}.\n")
            
            
            #   Código 11: Determinado para tratar o retorno da criação de um grupo.
            if req[:2] == '11':
                self.lastGroupAdded = req[2:15]
                if req[25:38] == self.codeUser:
                    print(f"\n Grupo criado com sucesso!\n")
                else:   
                    contactOrNot = "None"
                    for contact in self.getRegisteredContact():
                        if contact.split('-')[0] == req[25:38]:
                            contactOrNot = contact.split('-')[1]
                    if contactOrNot == 'None':
                        print(f"\n Você foi adicionado ao grupo: {req[2:15]} pelo usuário ({req[25:38]}) as {str(datetime.fromtimestamp(int(req[15:25]), tz=ZoneInfo('America/Sao_Paulo')))[11:16]}.\n")
                    else:
                        print(f"\n Você foi adicionado ao grupo: {req[2:15]} pelo {contactOrNot} as {str(datetime.fromtimestamp(int(req[15:25]), tz=ZoneInfo('America/Sao_Paulo')))[11:16]}.\n")
                
                print(f"\n Deseja adicionar o grupo aos seus contatos? (/sim)\n")