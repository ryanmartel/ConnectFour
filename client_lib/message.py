import json
import io
import selectors
import struct
import sys

class Message:
    def __init__(self, selector, sock, addr, request, logger):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.request = request
        self._buffer_in = b""
        self._buffer_out = b""
        self._queued = False
        self._header_len = None
        self.header = None
        self.response = None
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
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable
            self.logger.debug("BlockingIOError: Resource temporarily unavailable")
            pass
        else:
            if data:
                self._buffer_in += data
            else:
                self.logger.info("Connection Closed by server")
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._buffer_out:
            self.logger.debug(f"SENDING: {repr(self._buffer_out)} to {self.addr}")
            try:
                sent = self.sock.send(self._buffer_out)
            except BlockingIOError:
                self.logger.debug("BlockingIOError: Resource temporarily unavailable")
                pass
            else:
                self._buffer_out = self._buffer_out[sent:]

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
                io.BytesIO(json_bytes), encoding=encoding, newline=""
            )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(self, *, content_bytes, content_type, content_encoding):
        header = {
                "byteorder": sys.byteorder,
                "content-type": content_type,
                "content-encoding": content_encoding,
                "content-length": len(content_bytes)
        }
        header_bytes = self._json_encode(header, "utf-8")
        message_header = struct.pack(">H", len(header_bytes))
        message = message_header + header_bytes + content_bytes
        return message

    def _process_json_response(self):
        content = self.response
        result = content.get("result")
        print(result)

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
            if self.response is None:
                self.process_response()

    def write(self):
        if not self._queued:
            self.queue_request()

        self._write()

        if self._queued:
            if not self._buffer_out:
                # Set selector to listen for read events, we're done writing.
                self._set_selector_events_mask("r")

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



    def queue_request(self):
        content = self.request["content"]
        content_type = self.request["type"]
        content_encoding = self.request["encoding"]
        if content_type == "text/json":
            req = {
                    "content_bytes": self._json_encode(content, content_encoding),
                    "content_type": content_type,
                    "content_encoding": content_encoding,
                    }
        else:
            req = {
                    "content_bytes": content,
                    "content_type": content_type,
                    "content_encoding": content_encoding,
                    }
        message = self._create_message(**req)
        self._buffer_out += message
        self._queued = True


    def process_protoheader(self):
        hdrlen = 2
        if len(self._buffer_in) >= hdrlen:
            self._header_len = struct.unpack(
                ">H", self._buffer_in[:hdrlen]
            )[0]
            self._buffer_in = self._buffer_in[hdrlen:]


    def process_header(self):
        header_len = self._header_len
        if len(self._buffer_in) >= header_len:
            self.header = self._json_decode(self._buffer_in[:header_len], "utf-8")
            self._buffer_in = self._buffer_in[header_len:]
            for req in ("byteorder", "content-length", "content-type", "content-encoding"):
                if req not in self.header:
                    self.logger.error(f"Missing required header {req}")
                    raise ValueError("Missing required header")

    def process_response(self):
        content_len = self.header["content-length"]
        if not len(self._buffer_in) >= content_len:
            return
        data = self._buffer_in[:content_len]
        self._buffer_in = self._buffer_in[:content_len]
        if self.header["content-type"] == "text/json":
            encoding = self.header["content-encoding"]
            self.response = self._json_decode(data, encoding)
            self.logger.debug(f"received response {repr(self.response)} from {self.addr}")
            self._process_json_response()
        else:
            # Unknown content type
            self.response = data
            self.logger.warning(f"recieved unknown format response from {self.addr}")
        self.close()


