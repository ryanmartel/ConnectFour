import logging
import sys
import socket
import selectors
import traceback

from client_lib.message import Message


logger = logging.getLogger('CONNECT-FOUR CLIENT')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)
sel = selectors.DefaultSelector()

def create_request(action):
    if action == "ping":
        return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(action=action)
                )
    else:
        return dict(
                type="binary/custom-binary",
                encoding="binary",
                content=bytes(action, encoding="utf-8"),
                )
def main():
    if len(sys.argv) != 4:
        print("usage:", sys.argv[0], "<host> <port> <action>")
        sys.exit(1)

    host, port = sys.argv[1], int(sys.argv[2])
    action = sys.argv[3]
    request = create_request(action)
    addr = (host, port)
    logger.info(f"starting connection -> {host}, port: {port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = Message(sel, sock, addr, request, logger)
    sel.register(sock, events, data=message)

    try:
        while True:
            events = sel.select(timeout=1)
            for key, mask in events:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    logger.error(f"Error: exception for {message.addr}:\n{traceback.format_exc()}")
                    message.close()
            if not sel.get_map():
                break
    except KeyboardInterrupt:
        logger.info("Caught keyboard interrupt, exiting")
    finally:
        sel.close()
    

if __name__ == '__main__':
    main()

