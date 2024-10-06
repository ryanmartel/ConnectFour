import logging
import sys
import selectors
import socket

logger = logging.getLogger('CONNECT-FOUR SERVER')
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)
sel = selectors.DefaultSelector()

def main():
    if len(sys.argv) != 2:
        print("usage:", sys.argv[0], "<port>")
        sys.exit(1)

    port = int(sys.argv[1])
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Avoid bind() exception: OSError: [Errno 48] Address already in use
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind(('', port))
    lsock.listen()
    logger.info("listening on "+sys.argv[1])
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)
    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    message = key.data
                    try:
                        message.process_events(mask)
                    except Exception:
                        logger.error("Error: exception for ")
                        message.close()
    except KeyboardInterrupt:
        logger.info("Caught keyboard interrupt, exiting")
    finally:
        sel.close()

def accept_wrapper(sock):
    conn, addr = sock.accept()
    logger.info(f"Accepted connection from {addr}")
    conn.setblocking(False)

if __name__ == '__main__':
    main()
