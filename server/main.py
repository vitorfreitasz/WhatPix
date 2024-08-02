from server.Server import Server

HOST = "127.0.0.1"
PORT = 9070

if __name__ == "__main__":
    server = Server(HOST, PORT)
    server.start()