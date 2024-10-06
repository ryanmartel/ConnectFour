import logging
import sys
import socket
import selectors


logger = logging.getLogger('CONNECT-FOUR CLIENT')
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)
sel = selectors.DefaultSelector()

def main():
    if len(sys.argv) != 3:
        print("usage:", sys.argv[0], "<host> <port>")
        sys.exit(1)

    host, port = sys.argv[1], int(sys.argv[2])
    addr = (host, port)
    logger.info(f"starting connection -> {host}, port: {port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    # ADD MESSAGE
    sel.register(sock, events, data=None)

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    continue
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    logger.error("Error: excetion for ")
                    message.close()
    except KeyboardInterrupt:
        logger.info("Caught keyboard interrupt, exiting")
    finally:
        sel.close()
    

if __name__ == '__main__':
    main()

