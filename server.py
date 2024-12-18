import logging
import selectors
import socket
import json
import struct
import argparse

from server_lib.action import Action
from server_lib.message_handler import MessageHandler

class Server:
    def __init__(self, port: int, log_level) -> None:
        """Initialize server listening on the given port.
        Logger is configured as a stdout logger at the given level."""
        
        # Logging
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger = logging.getLogger('CONNECT-FOUR SERVER')
        self.logger.setLevel(log_level)
        self.logger.addHandler(ch)

        # Socket selectors
        self.port = port
        self.read_sel = selectors.DefaultSelector()
        self.write_sel = selectors.DefaultSelector()

        # Client map
        self.connected_clients = {}

        # Sending actions and receiving handler
        self.action = Action(self.logger)
        self.handler = MessageHandler(self.logger, self.action, self.write_sel, self.connected_clients)

    def start_server(self) -> None:
        """ Binding to accept connections from any routable address at the 
        given port. TCP socket."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.port))
        self.sock.listen()
        self.logger.info(f'Started Server at port {self.port}')
        self.read_sel.register(self.sock, selectors.EVENT_READ, self.accept_conn)
        
    def shutdown(self) -> None:
        """ Server shutdown. Just closes connections, clients 
        are left to handle this. """
        self.logger.info("Shutting down server")
        for conn in self.connected_clients.keys():
            conn.close()
        self.sock.close()

    def accept_conn(self, sock) -> None:
        """Accept incoming connections. Connections are refused when there are already
        two players connected, or the game is in the finished state. The game leaves 
        the finished state once all players disconnect from the game"""
        conn, addr = sock.accept()
        self.logger.info(f'Accepted client connection from host: {addr[0]}, port: {addr[1]}')

        if len(self.connected_clients) == 2:
            self.logger.warning(f'Too many clients! only two players are allowed. Removing last added client')
            conn.sendall(self.action.connection_refuse("Too many players"))
            conn.shutdown(socket.SHUT_RDWR)
            return
        if self.handler.game_finished():
            self.logger.warning(f'Attempted to connect to finished game. Refused')
            conn.sendall(self.action.connection_refuse("Players still exiting game"))
            conn.shutdown(socket.SHUT_RDWR)
            return

        # Register client information
        self.connected_clients[conn] = addr
        self.read_sel.register(conn, selectors.EVENT_READ, self.receive)
        self.write_sel.register(conn, selectors.EVENT_WRITE)
        self.handler.new_player_connected(addr)

    def receive(self, sock) -> None:
        """Receive loop for the server.
        Managed by selector"""
        bmsg_len = b""
        chunk = sock.recv(4)
        # Client has closed a connection
        if not chunk:
            self.closed_connection(sock)
            return

        bmsg_len += chunk
        # Ensure all 4 bytes have been read
        while (len(bmsg_len) != 4):
            chunk = sock.recv(4-len(bmsg_len))
            if not chunk:
                self.closed_connection(sock)
                return
            bmsg_len += chunk

        msg_len = struct.unpack('<i', bmsg_len)[0]
        msg = ""
        chunk = sock.recv(msg_len).decode("utf-8")
        # Client has closed a connection
        if not chunk:
            self.closed_connection(sock)
            return

        msg += chunk
        # Ensure the full message has been received
        while (len(msg) != msg_len):
            chunk = sock.recv(msg_len-len(msg)).decode("utf-8")
            if not chunk:
                self.closed_connection(sock)
                return
            msg += chunk

        json_msg = json.loads(msg)
        self.logger.debug(f'Received {json_msg} from client at {self.connected_clients.get(sock)}')
        self.handler.handle_message(json_msg, sock)

    def closed_connection(self, sock) -> None:
        """When an empty message was read on a ready socket.
        The client has closed the connection, and it should be removed
        from server"""
        self.logger.info(f'Client at {self.connected_clients.get(sock)} closed connection')
        addr = self.connected_clients.pop(sock)
        self.read_sel.unregister(sock)
        self.write_sel.unregister(sock)
        self.handler.remove_player(addr)


    def run(self) -> None:
        """Main loop for server. Manages selectors"""
        self.start_server()
        self.logger.info("Server is initialized")
        while True:
            for key, _ in self.read_sel.select():
                sock, cb = key.fileobj, key.data
                cb(sock)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--port", required=True, help="Port used to run the ConnectFour server", type=int)
    parser.add_argument("--loglevel", help="Log verbosity level: Default INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()
    loglevel = logging.INFO
    if args.loglevel == "DEBUG":
        loglevel = logging.DEBUG
    elif args.loglevel == "WARNING":
        loglevel = logging.WARNING
    elif args.loglevel == "ERROR":
        loglevel = logging.ERROR
    server = Server(args.port, loglevel)
    try:
        server.run()
    except KeyboardInterrupt:
        print('Interrupt signal received, shutting down')
        server.shutdown()
    except Exception as e:
        print('Unexpected error has occured, shutting down')
        server.shutdown()
