import logging
import struct
import sys
import argparse

import socket
import selectors
import threading
import os
import json

from client_lib.action import Action
from client_lib.tui import ConnectFour
from client_lib.message_handler import MessageHandler


class Client:

    def __init__(self, log_level, addr):
        self.logger = logging.getLogger('CONNECT-FOUR CLIENT')
        self.logger.setLevel(log_level)

        self.addr = addr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sel = selectors.DefaultSelector()

        self.action = Action(self.logger)
        self.ui = ConnectFour(self.sock, self.logger)
        self.handler = MessageHandler(self.logger, self.ui, self.sock)


    def connect(self):
        self.logger.info(f"Connecting to host: {self.addr[0]}, port: {self.addr[1]}")
        # Start receiving thread
        rec = threading.Thread(target=self.receive)
        self.sock.connect(self.addr)
        rec.start()
        # send connection message to server
        self.sock.sendall(self.action.connect())

        self.ui.run()
        # UI interface has exited, shutdown all threads.
        os._exit(0)

    def shutdown(self):
        self.logger.info("Shutting down client")
        self.sock.close()
        os._exit(0)


    def receive(self):
        while True:
            bmsg_len = self.sock.recv(4)
            if not bmsg_len:
                print(f'Server connection was lost! exiting...')
                os._exit(1)

            msg_len = struct.unpack('<i', bmsg_len)[0]
            msg = self.sock.recv(msg_len).decode("utf-8")
            # Server has unexpectadly closed
            if not msg:
                print(f'Server connection was lost! exiting...')
                os._exit(1)
            
            json_msg = json.loads(msg)
            self.handler.handle_message(json_msg)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", required=True, help="The ip address or DNS of the running ConnectFour server")
    parser.add_argument("-p","--port", required=True, help="Port used by the running ConnectFour server", type=int)
    parser.add_argument("--loglevel", help="Log verbosity level: Default INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()
    # Change logging level here. 
    loglevel = logging.INFO
    if args.loglevel == "DEBUG":
        loglevel = logging.DEBUG
    elif args.loglevel == "WARNING":
        loglevel = logging.WARNING
    elif args.loglevel == "ERROR":
        loglevel = logging.ERROR
    client = Client(loglevel, (args.ip, args.port))
    try:
        client.connect()
    except KeyboardInterrupt:
        print("Interrupt signal received, shutting down")
        client.shutdown()
    except Exception as e:
        print(f"Uncaught exception: {e}")

