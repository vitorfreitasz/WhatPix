class Connection:
    def __init__(self, conn, addr, server):
        super().__init__()
        self.connection = conn
        self.address = addr
        self.server = server
        self.online = True
        self.number = None
        
    def start(self):
        print(f'Connection created at {self.address}!')