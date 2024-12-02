# Connect-Four Game Example

This is a simple Connect-Four game implemented using Python and sockets. The GUI is provided through a textual terminal interface (TUI)
A requirements.txt file is provided with all dependencies needed to run the client and server.

## How to Run
**SERVER**  
`python server.py -p [port]`  
Where port is the desired port for the server to run. Ensure this port is open prior to starting the server.

**CLIENT**  
`python client.py -i [host] -p [port]`  
Where host is the host ip addr or DNS of the running server and port is the port that the server is running on.  

**Additional options**  
Both client and server support `-h` for help and `--loglevel [loglevel]` to change the minimum level event to be logged. The default
log level is 'INFO', available options are 'DEBUG', 'INFO', 'WARNING', 'ERROR'.

## Runtime Mechanics

### Logging
Logging is implemented in both the server and client. The server logs directly to STDOUT. The client logs to a log modal 
window in the TUI. This log modal can be opened/closed by pressing 'l' while the game is running.

### Game Message Protocol
All messages are passed over json. The command type is sent using the action field. additional fields may be present depending on the selected action. 
For example, a move action will also contain a field with the location of the move. The response sent from the server will contain a result field. 
This result field gives if the action was accepted or an error occurred.  
The server is also able to send broadcast messages to the client. these messages from the server use a broadcast field to either give clients changes to the game state or information
about other clients connecting or disconnecting.  
Each JSON message is preceded by a 4 byte integer which gives the length of the message sent.  
Upon connection, clients send a connect message to the server. The server then registers the client connection and returns a connected successfully message to the client.  

### Game state Synchronization
Game state is synchronized across clients by the server sending broadcast messages to all clients after each move. The
broadcast message is sent after every move request, even if it is an invalid move (which is rejected). This ensures that 
even if clients somehow become out of sync (causing their move to be rejected), they are re-synchronized at the next attempted move. 


## Gameplay
1. **Start the server:** Run the `server.py` script as shown above.
2. **Connect clients:** Run the `client.py` script on two different machines or terminals as shown above.
3. **Waiting for Players:** The game will not start until two players are connected to the server. Once
there are two players connected, the game will move to the Pregame state.
4. **Pregame:** Pregame is where players can write in a username for the game session. the input must be
   between 1 and 10 letters in length. Once both players enter their names the game will start!
6. **Play the game:** Players take turns entering their moves. The first player to get four in a row wins!
   The current player's turn is located above the game board. Once one player 

**Technologies used:**
* Python
* Sockets
* Textual

**Additional resources:**
* [Statement of Work](https://github.com/ryanmartel/ConnectFour/wiki/Statement-of-Work)
* [Python documentation](https://docs.python.org/3/)
* [sockets tutorial](https://docs.python.org/3/howto/sockets.html)
* [Textual documentation](https://textual.textualize.io/)
