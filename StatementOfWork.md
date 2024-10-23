# Statement of Work

### Project Title:
Connect Four

### Team:
Ryan Martel

### Project Objective:
Create a simple Connect-Four game that can be played by two players over sockets 
in python. There will be a server which allows up to two clients to connect to it at a time and start a game of connect four. The server/clients will only allow valid moves in the game and will gracefully handle any errors. The clients connect to the server using sockets in python. The first player to get four in a row wins.

### Scope:

#### Inclusions:
* Client-Server architecture. Clients will connect to a game server using python sockets.
* Two player. There will be no more than two clients allowed at a time. There will also be 
required to be two clients connected to start a game.
* Invalid game state, or illegal game moves will not be allowed by server. If an unexpected 
error is encountered, the server gracefully shuts down.
* Simple GUI through a Curses terminal interface
* CLI inputs and options. For client (-h help, -i IP of server, -p port of server, -n DNS name of server). For server (-h help, -i host-ip, -p port)

#### Exclusions:

* save state will not be included.

### Deliverables:

* Server script
* Client script
* requirements.txt (to ensure all libraries available)
* README with full game instructions

### Timeline:

#### Key Milestones:

* Sprint 0: Setup Tools, SOW (this document) 22-Sep
* Sprint 1: Socket Programming, TCP Client Server 06-Oct
* Sprint 2: Develop Game Message Protocol, Manage Client Connections 20-Oct
* Sprint 3: Multi-player functionality, Synchronize state across clients 03-Nov
* Sprint 4: Game Play, Game State 17-Nov
* Sprint 5: Implement Error Handling and Testing 06-Dec

#### Task Breakdown:

1. Create echo server and client with sockets. -- 30 min
2. Create CLI for script options -- 2 hours
3. Create main gameplay event loop -- 3 days
4. Create GUI -- 2 days
5. Allow exactly two connections to server and give user-friendly error message on more connection requests -- 1 day
6. Synchronize state among clients -- 3 days.
7. Ensure game conditions for winning/draws are handled correctly -- 2 days
8. Ensure graceful error handling on lost connection, or network instability. -- 2 days
9. Ensure appropriate test coverage, and run through the game -- 3 days

### Technical Requirements:

#### Hardware:

* Server
* 2 Clients 
* Appropriate network connection to allow client connection to server.

#### Software:

* Git
* Vim
* Unix-based OS
* Python libraries (sockets, etc std libraries)
* Python Curses library GUI

### Assumptions:

* Network connection is available between clients and server. 
* Terminal Curses Gui capability is available on clients

### Roles and Responsibilities:

**TEAM MEMBER**: Ryan Martel -- All responsibility

### Communication Plan:

This is a single-person team. There should not be difficulties in communication or conflict in meeting times.

### Additional Notes:

requirements.txt will be provided, as this project uses libraries external to python standard provided modules. 

