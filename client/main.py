from Client import Client

HOST = "127.0.0.1"
PORT = 9070

if __name__ == "__main__":
    server = Client(HOST, PORT)
    server.start()