import logging
import sys
import selectors
import socket
import json

from server_lib import action

class Server:
    def __init__(self, port, log_level):
        # Logger options
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger = logging.getLogger('CONNECT-FOUR SERVER')
        self.logger.setLevel(log_level)
        self.logger.addHandler(ch)

        self.port = port
        self.sock = None
        self.read_sel = selectors.DefaultSelector()
        self.write_sel = selectors.DefaultSelector()

        self.connected_clients = {}
        self.game = Game()

    def start_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.port))
        self.sock.listen()
        self.logger.info(f'Started Server at port {self.port}')
        self.read_sel.register(self.sock, selectors.EVENT_READ, self.accept_conn)

    def accept_conn(self, sock):
        conn, addr = sock.accept()
        self.logger.info(f'Accepted client connection from host: {addr[0]}, port: {addr[1]}')
        self.connected_clients[conn] = addr
        self.read_sel.register(conn, selectors.EVENT_READ, self.receive)
        self.write_sel.register(conn, selectors.EVENT_WRITE)
        self.broadcast(action.connection_start(addr))

    def receive(self, sock):
        msg = sock.recv(1024).decode("utf-8")

        # Client has closed a connection
        if not msg:
            self.logger.info(f'Client at {self.connected_clients.get(sock)} closed connection')
            addr = self.connected_clients.pop(sock)
            self.read_sel.unregister(sock)
            self.write_sel.unregister(sock)
            self.broadcast(action.connection_end(addr))
            return

        json_msg = json.loads(msg)
        self.logger.debug(f'Received {json_msg} from client at {self.connected_clients.get(sock)}')
        response = action.handle_message(json_msg)
        if response is not None:
            sock.sendall(response)

    def broadcast(self, msg):
        for key, _ in self.write_sel.select(0):
            key.fileobj.send(msg)

    def run(self):
        self.start_server()
        self.logger.info("Server is initialized")
        while True:
            for key, _ in self.read_sel.select():
                sock, cb = key.fileobj, key.data
                cb(sock)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage:", sys.argv[0], "<port>")
        sys.exit(1)
    try:
        port = int(sys.argv[1])
        server = Server(port, logging.DEBUG)
        server.run()
    except ValueError:
        print('Invalid port entered. Expected Integer')
