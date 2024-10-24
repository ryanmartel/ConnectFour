import logging
import sys
import socket
import selectors
import threading
import os
import json

from client_lib.action import Action
from client_lib.tui import run


class Client:
    def __init__(self, log_level, addr):
        # Logger options
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        self.logger = logging.getLogger('CONNECT-FOUR CLIENT')
        self.logger.setLevel(log_level)
        self.logger.addHandler(ch)
        self.addr = addr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sel = selectors.DefaultSelector()
        self.action = Action(self.logger)

    def connect(self):
        self.logger.info(f"Connecting to host: {self.addr[0]}, port: {self.addr[1]}")
        self.sock.connect(self.addr)
        # send connection message to server
        self.sock.sendall(self.action.connect())
        # Start Repl
        cin = threading.Thread(target=self.repl)
        cin.start()
        # Start curses tui ui
        ui = threading.Thread(target=run)
        ui.start()
        # continue to receive on this thread
        while True:
            self.receive()


    def receive(self):
        msg = self.sock.recv(1024).decode("utf-8")
        # Server has unexpectadly closed
        if not msg:
            self.logger.error(f'Server connection was lost! exiting...')
            os._exit(1)

        json_msg = json.loads(msg)
        self.action.handle_message(json_msg)
        # Exceeds max allowed player count
        if json_msg.get("result") == "connection" and json_msg.get("status") == "refused":
            self.logger.error('Too Many clients currently in game. Max allowed is 2')
            os._exit(1)

    # This may be able to be brought into the curses interface as it can handle input without blocking
    def repl(self):
        while True:
            msg = input('>>> ')
            if msg == "exit":
                os._exit(0)
            elif msg == "ping":
                self.sock.sendall(self.action.ping())
            else:
                print(msg)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("usage:", sys.argv[0], "<host> <port>")
        sys.exit(1)
    # try:
        # Change logging level here. 
    client = Client(logging.DEBUG, (sys.argv[1], int(sys.argv[2])))
    client.connect()
    # except ValueError:
    #     print('Invalid port entered. Expected Integer')


