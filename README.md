# Connect-Four Game

This is a simple Connect-Four game implemented using Python and sockets. The GUI is provided through a textual terminal interface (TUI)
A requirements.txt file is provided with all dependencies needed to run the client and server. Python version of at least 3.10 is required. 
The python-version.txt file included in the directory includes this version number. This is the python version that was tested on the 
CSU dept machines.

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

**Additional Information**  
On the CSU dept machines, the highest python interpreter available is 3.10. For running on the CSU dept machines this is the 
only version of the interpreter that will work. To ensure the 3.10 interpreter is available, load the module using  
`module load python/bundle-3.10`  
This module and interpreter do not support the `python` command, and instead the server and client will have to be started 
using the `python3` command with the same options.

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
6. **Play the game:** Players take turns entering their moves. The first player to get four in a row wins! Use the
   arrow keys and press enter to select the column to play to. Alternatively, you can use the mouse to click on the
   column button. The current player's turn is located above the game board. Once one player gets four in a row, or the game board
   is full (a draw) the game will enter the finished state.
8. **Exit the game:** In the finished state, the message above the board will reflect the winner of the game (or draw if one
   occured). Press 'q' to quit the game. New players can not connect to the server until both players have exited
   from a finished game.

## Additional Information

### Security/Risk Evaluation  
Some security/risks of this application  
1. Unencrypted traffic. All information is sent over plaintext for anyone to intercept and read. This is not too concerning
   for this application since the data is not sensitive.
2. DoS attacks. The server does not limit rate of connections and could be flooded with attempted connections causing the
   server to be overwhelmed.
3. Modified requests. The server could be given modified requests following the correct protocol to place the game in an unexpected state or
   crash the server.

### Roadmap on where I would take project from here
Features that I would like to implement or improve on are:
* Cleaner UI. With more work on the CSS files, the board could look a lot nicer.
* Implement chat for players. It would be nice for players to communicate with each other during the game.
* Implement a single-player option. Connect four is a well known space for search-based AI algorithms such as alpha-beta search and expectimax.
  It would be a great exercise to implement a basic AI player option for the game.
### Retrospective on overall project
1. **What went right** The UI library that I chose (Textual) was a significant learning investment, but I believe that it paid off.
   The library had built-in async support for updating the screen and taking user input, which worked very well when sending messages
   from a separate thread receiving socket messages. I used the included async support to simplify many of my concurrency issues on
   the client side.
2. **What could be improved on** The UI design could be improved on. I did not have the extra time to really tweak the CSS to the point that I was happy with it. I also would have liked to have time to improve the error messages to the client. Right now they appear as a line of text beneath who's turn it is. I would have liked certain serious errors such as server failure to be contained in their own popups so that the user is forced to acknowledge them before the game exits.

**Technologies used:**
* Python
* Sockets
* Textual

**Additional resources:**
* [Statement of Work](https://github.com/ryanmartel/ConnectFour/wiki/Statement-of-Work)
* [Python documentation](https://docs.python.org/3/)
* [sockets tutorial](https://docs.python.org/3/howto/sockets.html)
* [Textual documentation](https://textual.textualize.io/)
