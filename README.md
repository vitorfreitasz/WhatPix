# WhatPix
<p align="justify ">
Repositório criado para armazenar o trabalho da disciplina de Redes de Computadores. O trabalho consiste em uma aplicação para envio/troca de mensagens, que utiliza Sockets e um protocolo de comunicação específico.
</p>
<br>

## Como rodar?
- Rode `python server/main.py` Para rodar o servidor da aplicação.
- Rode `python client/main.py` Para rodar cada cliente.

## Funcionalidades

- `Cadastro`

- `Login`

- `Envio de mensagens privadas`

- `Criação de grupos`

- `Sistema de confirmação de entrega e confirmação de leitura de mensagens`

- `Armazenamento de mensagens para usuários que estão offline`

- `Armazenamento do histórico de mensagens por parte do cliente`

- `Criação de lista de contatos`

## Arquitetura

O projeto está configurado na seguinte arquitetura de páginas:

```
WhatPix/        Diretório geral.
│
├── client/                Diretório de arquivos do cliente.  
│   ├── db/                     Diretório do banco de dados do cliente.
│   │   └── contacts.json           Arquivo Json que armazena os dados da lista de contato dos clientes.
│   │     
│   ├── main.py             Arquivo que inicia o serviço do lado do cliente.
│   └── Client.py           Arquivo principal, que armazena toda lógica de gerenciamento de um cliente.
│ 
├── server/                 Diretório de arquivos do servidor. 
│   ├── config/                 Diretório de arquivos de configuração (do logger específicamente). 
│   │   └── logger.py               Arquivo o código do gerenciamento dos logs. 
│   │   
│   ├── db/                         Diretório do banco de dados do servidor. 
│   │   ├── awaitingMessages.json       Arquivo Json que armazena as mensagens a clientes registrados que estavam offline.
│   │   ├── groups.json                 Arquivo Json que armazena os dados os grupos criados e seus respectivos membros.
│   │   └── registeredUsers.csv         Arquivo CSV que armazena todos os clientes cadastrados.
│   │
│   ├── Server.py           Arquivo principal, que armazena a lógica de gerenciamento do servidor.
│   ├── Connection.py       Arquivo que armazena a classe que gerencia cada conexão com o servidor.
│   └── main.py             Arquivo que inicia o servidor.
│
├── README.md               Arquivo de documentação.
├── .gitignore              Arquivo que administra os arquivos que irão ou não ser enviados ao repositório.
└── Trabalho 1.pdf          Arquivo PDF com a especificação do protocolo.
```