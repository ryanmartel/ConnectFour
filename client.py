import logging
import struct
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

    def __init__(self, log_level, addr) -> None:
        """Initialize client and connect to server at given address
        Logger is configured later as part of TUI"""

        # Logging
        self.logger = logging.getLogger('CONNECT-FOUR CLIENT')
        self.logger.setLevel(log_level)

        # Selector
        self.addr = addr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sel = selectors.DefaultSelector()

        # Sending actions, UI, nad receiving handler
        self.action = Action(self.logger)
        self.ui = ConnectFour(self.sock, self.logger)
        self.handler = MessageHandler(self.logger, self.ui, self.sock)


    def connect(self) -> None:
        """Connect to the server and start the receiving thread
        Start the UI (BLOCKING)"""
        self.logger.info(f"Connecting to host: {self.addr[0]}, port: {self.addr[1]}")
        # Start receiving thread
        rec = threading.Thread(target=self.receive)
        self.sock.connect(self.addr)
        rec.start()
        # send connection message to server
        self.sock.sendall(self.action.connect())

        exit_val = self.ui.run()
        # UI interface has exited, shutdown all threads.
        if exit_val is None:
            os._exit(0)
        else:
            rec.join()
            print('Server connection was lost! exiting...')


    def shutdown(self) -> None:
        """Shutdown the client."""
        self.logger.info("Shutting down client")
        self.sock.close()
        os._exit(0)


    def receive(self) -> None:
        """Receive loop for the client.
        Ran in separate thread"""
        while True:
            bmsg_len = b""
            chunk = self.sock.recv(4)
            if not chunk:
                self.closed_connection()
            bmsg_len += chunk
            # Ensure all 4 bytes have been read
            while (len(bmsg_len) != 4):
                chunk = self.sock.recv(4-len(bmsg_len))
                if not chunk:
                    self.closed_connection()
                bmsg_len += chunk

            msg_len = struct.unpack('<i', bmsg_len)[0]
            msg = ""
            chunk = self.sock.recv(msg_len).decode("utf-8")
            # Server has unexpectadly closed
            if not chunk:
                self.closed_connection()
            msg += chunk
            # Ensure the full message has been received
            while (len(msg) != msg_len):
                chunk = self.sock.recv(msg_len-len(msg)).decode("utf-8")
                if not chunk:
                    self.closed_connection()
                msg += chunk
            
            json_msg = json.loads(msg)
            self.handler.handle_message(json_msg)

    def closed_connection(self) -> None:
        """When an empty message was read on socket.
        Server has closed the connection, and this client should exit"""
        self.ui.exit(True)
        exit()


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
    except Exception:
        print("Unexpected error has occured. Exiting application.")

