import logging
from socket import socket
from typing import cast
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
from textual.validation import Length
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, Input, Label, Log, Static

from client_lib.action import Action
from client_lib.users import Users


class Waiting(Screen):
    """The waiting screen diaplayed when less than two clients are connected"""

    CSS_PATH = "./styles/waiting.css"

    BINDINGS = [
            Binding("q", "app.quit", "Quit"),
            Binding("l", "logs", "Open/Close Logs")
            ]

    def compose(self) -> ComposeResult:
        """Compose the waiting screen"""
        yield Header()
        yield Vertical(WaitingStatus(id="dialog"))
        yield Footer()

    def action_logs(self) -> None:
        """Open the log modal"""
        self.app.push_screen(LogModal())

class WaitingStatus(Widget):
    """Container for game status items"""
    disconnect = reactive("Waiting on other player...")

    def render(self) -> str:
        """Render the waiting screen message"""
        return f"{self.disconnect}"

class Pregame(Screen):
    """The pregame screen to collect username"""

    CSS_PATH = "./styles/pregame.css"

    def compose(self) -> ComposeResult:
        """Compose the pregame screen"""
        yield Vertical(
            Input(placeholder="Enter your desired name",
                  validators=[
                      Length(minimum=1, maximum=10)
                      ],
                  id="input"
                  ),
            Label("Press 'Enter' to continue", id="hint"),
            id="dialog",
            )

class LogModal(ModalScreen):
    """Modal window to show logs"""

    logs = []

    BINDINGS = [
            Binding("l, escape", "exit_modal", "Exit Logs"),
            Binding("p", "app.ping", "send ping"),
            ]

    def compose(self) -> ComposeResult:
        """Compose the log modal"""
        yield LogMessage(id="logmodal")

    def action_exit_modal(self) -> None:
        """Close the log modal"""
        self.app.pop_screen()

class LogMessage(Static):
    """The log message holder widget"""

    BORDER_TITLE = "Logs"
    BORDER_SUBTITLE = "Press Esc or l to exit"

    def compose(self) -> ComposeResult:
        """Compose the log message holder"""
        yield Log(id="logger")

    def on_mount(self) -> None:
        """When this is mounted populate it with the logs"""
        log = self.query_one(Log)
        logs = LogModal.logs
        for line in logs:
            log.write_line(line)

class ColumnButton(Button):
    """Select button for column to play at"""

    @staticmethod
    def at(col: int) -> str:
        """Returns the ID of the button at given location"""
        return f"colbutton-{col}"

    def __init__(self, col: int) -> None:
        super().__init__(f"{col}", id=self.at(col))
        self.col = col


class Cell(Static):
    """Playable spaces in the game board"""

    @staticmethod
    def at(row: int, col: int) -> str:
        """Returns the ID of the button at given location"""
        return f"colbutton-{col}-{row}"

    def __init__(self, row: int, col: int) -> None:
        super().__init__("", id=self.at(row, col))

class GameGrid(Widget):
    """Main playable grid of cells"""

    def compose(self) -> ComposeResult:
        """Compose the game grid"""
        for row in reversed(range(Game.ROWS)):
            for column in range(Game.COLUMNS):
                yield Cell(row, column)

class Game(Screen):
    """The main game screen"""

    ROWS = 6
    COLUMNS = 7

    BINDINGS = [
            Binding("left", "navigate(-1)", "Move Left", False),
            Binding("right", "navigate(1)", "Move Right", False),
            Binding("q", "app.quit", "Quit"),
            Binding("l", "logs", "Open/Close Logs")
            ]


    class MakeLog(Message):
        """Make a log message."""

        def __init__(self, line: str, severity: str,) -> None:
            self.line = line
            self.severity = severity
            super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the game screen"""
        yield Header()
        yield GameRun()
        yield Footer()

    def column_button(self, col: int) -> ColumnButton:
        """Get the button at this location"""
        return self.query_one(f"#{ColumnButton.at(col)}", ColumnButton)

    def cell(self, row: int, col: int) -> Cell:
        """Get cell at given position"""
        return self.query_one(f"#{Cell.at(row,col)}", Cell)

    def color_cell(self, col: int, row: int, value: int) -> None:
        """set the color of the cell according to the value"""
        if 0 <= row <= 6 and 0 <= col <= 7:
            if value == 1:
                self.cell(row,col).set_class(True, "red")
            elif value == -1:
                self.cell(row,col).set_class(True, "blue")
            else:
                self.cell(row,col).remove_class("red", "blue")



    def action_logs(self) -> None:
        """Open the log modal"""
        self.app.push_screen(LogModal())

    def action_navigate(self, column: int) -> None:
        """Navigate to column indicator by offset"""
        self.post_message(self.MakeLog(f"Move at {column}", "debug"))
        if isinstance(self.focused, ColumnButton):
            self.set_focus(self.column_button((self.focused.col + column) % self.COLUMNS))

class GameHeader(Widget):
    """Header for the game"""

    def compose(self) -> ComposeResult:
        """Compose the game header"""
        with Horizontal():
            yield Label(self.app.title, id="app-title")
    
class GameRun(Widget):
    """The container widget for the game area"""

    def compose(self) -> ComposeResult:
        """Compose the game area"""
        yield GameStatus()
        yield GameGrid()
        yield ButtonGrid()



class GameStatus(Widget):
    """Container for game status items"""

    status = reactive("Next Turn: ")
    who = reactive("")
    err_msg = reactive("")
    exit_msg = reactive("")

    def render(self) -> str:
        """Render the game status"""
        return f"{self.status}{self.who}\n{self.exit_msg}\n{self.err_msg}"




class ButtonGrid(Widget):
    """Buttons for column selection"""

    def compose(self) -> ComposeResult:
        """Compose the selectable column buttons"""
        for column in range(Game.COLUMNS):
            yield ColumnButton(column)
            # yield Static(f"{column}", classes="selectbox")

class ListHandler(logging.Handler):
    """The list handler passed into the logger"""

    def __init__(self, log_list):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Our custom argument
        self.log_list = log_list

    def emit(self, record):
            # record.message is the log message
        self.log_list.append(self.format(record)) 

class ConnectFour(App):
    """The main TUI application"""

    ENABLE_COMMAND_PALETTE = False
    TITLE = "Connect Four"
    CSS_PATH = "./styles/styles.css"
    MODES = {
            "waiting": Waiting,
            "pregame": Pregame,
            "game": Game,
            "logs": LogModal,
            }
    turn_count = reactive(1)
    board = reactive({})

    class PregameMessage(Message):
        """TUI message to set Pregame state"""
        def __init__(self) -> None:
            super().__init__()

    class WaitingMessage(Message):
        """TUI message to set Waiting state"""
        def __init__(self, disconnect_status: bool) -> None:
            self.disconnect_status = disconnect_status
            super().__init__()

    class RunMessage(Message):
        """TUI message to set Run state and initialize users"""
        def __init__(self, users: Users, board: dict) -> None:
            self.users = users
            self.board = board
            super().__init__()

    class StatusMessage(Message):
        """TUI game status update message"""
        def __init__(self, turn_count: int, mover_host: str, mover_port: int, board: dict) -> None:
            self.turn_count = turn_count
            self.mover_host = mover_host
            self.mover_port = mover_port
            self.board = board
            super().__init__()

    class WinnerMessage(Message):
        """TUI game winner message"""
        def __init__(self, winner_host: str, winner_port: int, board: dict) -> None:
            self.winner_host = winner_host
            self.winner_port = winner_port
            self.board = board
            super().__init__()

    class DrawMessage(Message):
        """TUI game draw message"""
        def __init__(self, board: dict) -> None:
            self.board = board
            super().__init__()

    class MoveMessage(Message):
        """TUI move success message"""
        def __init__(self) -> None:
            super().__init__()

    class MoveErrorMessage(Message):
        """TUI move error message for user"""
        def __init__(self, err: str) -> None:
            self.err = err
            super().__init__()


    def __init__(self, sock: socket, logger: logging.Logger) -> None:
        super().__init__()
        self.logger = logger
        self.sock = sock
        self.action = Action(self.logger)
        # Set up logger
        lh = ListHandler(LogModal.logs)
        lh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        lh.setFormatter(formatter)
        self.logger.addHandler(lh)

    def on_button_pressed(self, event: ColumnButton.Pressed) -> None:
        """One of the column selection buttons was pressed"""
        button = cast(ColumnButton, event.button)
        self.action_move(button.col)

    def on_game_make_log(self, message: Game.MakeLog) -> None:
        """A log line is being made"""
        if message.severity == "info":
            self.logger.info(message.line)
        elif message.severity == "debug":
            self.logger.debug(message.line)
        elif message.severity == "error":
            self.logger.error(message.line)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """The user has submitted their requested name. async to ensure
        the proper waiting message is displayed"""
        # Ensure that the input passes validation check
        if event.validation_result is not None:
            if not event.validation_result.is_valid:
                return
        self.action_name(event.value)
        await self.switch_mode("waiting")
        status = self.query_one(WaitingStatus) 
        status.disconnect = "Waiting on other player..."

    def on_connect_four_status_message(self, message: StatusMessage) -> None:
        """The game status update message. Used to update the game board and 
        ensure the right game state is used for future turns"""
        try:
            game = self.query_one(Game)
        except NoMatches:
            # Can not update game with log screen present
            self.pop_screen()
            game = self.query_one(Game)
        self.logger.debug("received status message")
        self.turn_count = message.turn_count
        self.board = message.board
        for loc, value in self.board.items():
            game.color_cell(loc[0], loc[1], value)
        # Update the next mover
        self.query_one(GameStatus).who = self.users.get_mover_name(message.mover_host, message.mover_port)

    def on_connect_four_winner_message(self, message: WinnerMessage) -> None:
        """The game was won. enter the finished state and display winner"""
        try:
            game = self.query_one(Game)
        except NoMatches:
            # Can not update game with log screen present
            self.pop_screen()
            game = self.query_one(Game)
        self.logger.info("Game won!, setting finished")
        # Disable input buttons. Game is over
        for button in self.query(ColumnButton):
            button.disabled = True
        self.board = message.board
        for loc, value in self.board.items():
            game.color_cell(loc[0], loc[1], value)
        # Winner was the last player
        winner = self.users.get_mover_name(message.winner_host, message.winner_port)
        status = self.query_one(GameStatus)
        status.who = f"{winner}!"
        status.status = "The Winner is: "
        status.exit_msg = "Press 'q' to quit"

    def on_connect_four_draw_message(self, message: DrawMessage) -> None:
        """The game ended in a draw."""
        try:
            game = self.query_one(Game)
        except NoMatches:
            # Can not update game with log screen present
            self.pop_screen()
            game = self.query_one(Game)
        self.logger.info("Game was a draw, setting finished")
        # Disable input buttons. Game is over
        for button in self.query(ColumnButton):
            button.disabled = True
        self.board = message.board
        for loc, value in self.board.items():
            game.color_cell(loc[0], loc[1], value)
        status = self.query_one(GameStatus)
        status.who = ""
        status.status = "The game was a draw!"
        status.exit_msg = "Press 'q' to quit"



    def on_connect_four_pregame_message(self, message: PregameMessage) -> None:
        """Change state to pregame to collect user name"""
        self.logger.info("TUI setting pregame")
        self.switch_mode("pregame")

    async def on_connect_four_waiting_message(self, message: WaitingMessage) -> None:
        """Change state to waiting. If this was due to an unexpected client disconnection
        then set the appropriate waiting message"""
        self.logger.info("TUI setting waiting")
        disconnect_status = message.disconnect_status
        await self.switch_mode("waiting")

        status = self.query_one(WaitingStatus) 
        if disconnect_status:
            status.disconnect = "The other player has disconnected. Waiting for another player"
        else:
            status.disconnect = "Waiting on other player..."


    async def on_connect_four_run_message(self, message: RunMessage) -> None:
        """Run message received. Game is starting. Async to ensure that the game screen is 
        loaded before attempting to initialize the cells and place first player in status"""
        self.logger.info("TUI setting run")
        self.users = message.users
        await self.switch_mode("game")
        self.query_one(GameStatus).who = self.users.first.name
        self.board = message.board
        game = self.query_one(Game)
        for loc, value in self.board.items():
            game.color_cell(loc[0], loc[1], value)

    def on_connect_four_move_error_message(self, message: MoveErrorMessage) -> None:
        """The attempted move was rejected by the server because it was invalid
        update the game status to reflect error and inform user"""
        try:
            game = self.query_one(Game)
        except NoMatches:
            self.pop_screen()
        self.logger.info(f"Error on move: {message.err}")
        status = self.query_one(GameStatus)
        status.err_msg = message.err

    def on_connect_four_move_message(self, message: MoveMessage) -> None:
        """The attempted move was accepted by the server. Clear
        any previous error status messages"""
        try:
            game = self.query_one(Game)
        except NoMatches:
            self.pop_screen()
        self.logger.debug("Sucessful move response")
        status = self.query_one(GameStatus)
        status.err_msg = ""



    def on_mount(self) -> None:
        """Start the game in the waiting state"""
        self.switch_mode("waiting")

    def action_move(self, col: int) -> None:
        """Send a move to the server at the desired location"""
        self.sock.sendall(self.action.move(col, self.turn_count))

    def action_name(self, name: str) -> None:
        """Send the server this user's selected user name"""
        self.sock.sendall(self.action.set_name(name))

