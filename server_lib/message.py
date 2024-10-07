import sys
import selectors
import json
import io
import struct
import time

class Message:
    def __init__(self, selector, sock, addr, logger):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._buffer_in = b""
        self._buffer_out = b""
        self._header_len = None
        self.header = None
        self.request = None
        self.response_created = False
        self.logger = logger

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            self.logger.error(f"Invalid events mask mode {repr(mode)}")
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            self.logger.debug("BlockingIOError: Resource temporarily unavailable")
            pass
        else:
            if data:
                self._buffer_in += data
            else:
                self.logger.info(f"Connection Closed by client at {self.addr}")
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._buffer_out:
            self.logger.debug(f"SENDING: {repr(self._buffer_out)} to {self.addr}")
            try:
                # Should be ready to write
                sent = self.sock.send(self._buffer_out)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                self.logger.debug("BlockingIOError: Resource temporarily unavailable")
                pass
            else:
                self._buffer_out = self._buffer_out[sent:]
                # Close when the buffer is drained. The response has been sent.
                if sent and not self._buffer_out:
                    self.close()

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(
        self, *, content_bytes, content_type, content_encoding
    ):
        header = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        header_bytes = self._json_encode(header, "utf-8")
        message_hdr = struct.pack(">H", len(header_bytes))
        message = message_hdr + header_bytes + content_bytes
        return message

    def _create_response_json_content(self):
        if self.request:
            action = self.request.get("action")
            if action == "ping":
                answer = "pong"
                content = {"result": answer}
                content_encoding = "utf-8"
                response = {
                    "content_bytes": self._json_encode(content, content_encoding),
                    "content_type": "text/json",
                    "content_encoding": content_encoding,
                }
                return response
        else:
            content = {"result": f'Error: invalid action.'}
            content_encoding = "utf-8"
            response = {
                "content_bytes": self._json_encode(content, content_encoding),
                "content_type": "text/json",
                "content_encoding": content_encoding,
            }
            return response

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()

        if self._header_len is None:
            self.process_protoheader()

        if self._header_len is not None:
            if self.header is None:
                self.process_header()

        if self.header:
            if self.request is None:
                self.process_request()

    def write(self):
        if not self.response_created:
            self.create_response()

        self._write()

    def close(self):
        self.logger.info(f"Closing connection to {self.addr}")
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            self.logger.error(f"selector.unregister() exception for {self.addr}: {repr(e)}")
        try:
            self.sock.close()
        except OSError as e:
            self.logger.error(f"socket.close() exception for {self.addr}: {repr(e)}")
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    def process_protoheader(self):
        hdrlen = 2
        if len(self._buffer_in) >= hdrlen:
            self._header_len = struct.unpack(
                ">H", self._buffer_in[:hdrlen]
            )[0]
            self._buffer_in = self._buffer_in[hdrlen:]

    def process_header(self):
        hdrlen = self._header_len
        if len(self._buffer_in) >= hdrlen:
            self.header = self._json_decode(
                self._buffer_in[:hdrlen], "utf-8"
            )
            self._buffer_in = self._buffer_in[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.header:
                    self.logger.error(f"Missing required header {reqhdr}")
                    raise ValueError(f'Missing required header "{reqhdr}".')

    def process_request(self):
        content_len = self.header["content-length"]
        if not len(self._buffer_in) >= content_len:
            return
        data = self._buffer_in[:content_len]
        self._buffer_in = self._buffer_in[content_len:]
        if self.header["content-type"] == "text/json":
            encoding = self.header["content-encoding"]
            self.request = self._json_decode(data, encoding)
            self.logger.debug(f"received request {repr(self.request)} from {self.addr}")
        else:
            # unknown content-type
            # self.request = data
            self.logger.warning(f"recieved unknown format request from {self.addr}")
        # Set selector to listen for write events, we're done reading.
        self._set_selector_events_mask("w")

    def create_response(self):
        response = self._create_response_json_content()
        message = self._create_message(**response)
        self.response_created = True
        self._buffer_out += message


