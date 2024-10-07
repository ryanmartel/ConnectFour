# Connect-Four Game Example

This is a simple Connect-Four game implemented using Python and sockets. The GUI is provided through a simple web interface.

**Current Status:**
Currently server.py and client.py only set up a TCP connection and send simple messages from client to server.
starting `client.py` with `host port ping` will return the response `pong` to the client.  All other arguments will 
return a graceful error response and exit the client.  

Logging is implemented and while in development is set to DEBUG mode. This will show the raw message contents both sent and 
received on the server and client

**How to play:**
1. **Start the server:** Run the `server.py` script.
2. **Connect clients:** Run the `client.py` script on two different machines or terminals.
3. **Play the game:** Players take turns entering their moves. The first player to get four in a row wins!

**Technologies used:**
* Python
* Sockets

**Additional resources:**
* [Statement of Work](https://github.com/ryanmartel/ConnectFour/wiki/Statement-of-Work)
* [Python documentation](https://docs.python.org/3/)
* [sockets tutorial](https://docs.python.org/3/howto/sockets.html)
    
