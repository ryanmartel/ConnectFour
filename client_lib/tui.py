import logging
from typing import cast
from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
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
        yield Vertical(
                Label("waiting on other player...", id="waiting_on"),
                id="dialog"
                )
        yield Footer()

    def action_logs(self) -> None:
        self.app.push_screen(LogModal())

class Pregame(Screen):
    """The pregame screen to collect username"""

    CSS_PATH = "./styles/pregame.css"

    def compose(self) -> ComposeResult:
        yield Vertical(
            Input(placeholder="Enter your desired name", max_length=10, id="input"),
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
        # yield Static("logs", id="logmodal")
        yield LogMessage(id="logmodal")

    def action_exit_modal(self) -> None:
        self.app.pop_screen()

class LogMessage(Static):


    BORDER_TITLE = "Logs"
    BORDER_SUBTITLE = "Press Esc or l to exit"

    def compose(self) -> ComposeResult:
        yield Log(id="logger")

    def on_mount(self) -> None:
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
        for row in reversed(range(Game.ROWS)):
            for column in range(Game.COLUMNS):
                yield Cell(row, column)
    # yield Static(f"{row}-{column}", classes="gridbox")

class Game(Screen):

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
        self.app.push_screen(LogModal())

    def action_navigate(self, column: int) -> None:
        """Navigate to column indicator by offset"""
        self.post_message(self.MakeLog(f"Move at {column}", "debug"))
        if isinstance(self.focused, ColumnButton):
            self.set_focus(self.column_button((self.focused.col + column) % self.COLUMNS))

class GameHeader(Widget):
    """Header for the game"""
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(self.app.title, id="app-title")
    
class GameRun(Widget):


    def compose(self) -> ComposeResult:
        yield GameStatus()
        yield GameGrid()
        yield ButtonGrid()



class GameStatus(Widget):
    """Container for game status items"""
    status = reactive("Next Turn: ")
    who = reactive("")
    exit_msg = reactive("")

    def render(self) -> str:
        return f"{self.status}{self.who}\n{self.exit_msg}"




class ButtonGrid(Widget):
    """Buttons for row selection"""
    def compose(self) -> ComposeResult:
        for column in range(Game.COLUMNS):
            yield ColumnButton(column)
            # yield Static(f"{column}", classes="selectbox")

class ListHandler(logging.Handler):
    def __init__(self, log_list):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Our custom argument
        self.log_list = log_list
    def emit(self, record):
            # record.message is the log message
        self.log_list.append(self.format(record)) 

class ConnectFour(App):
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
        def __init__(self) -> None:
            super().__init__()

    class RunMessage(Message):
        """TUI message to set Run state and initialize users"""
        def __init__(self, users: Users, board) -> None:
            self.users = users
            self.board = board
            super().__init__()

    class StatusMessage(Message):
        """TUI game status update message"""
        def __init__(self, turn_count, mover_host, mover_port, board):
            self.turn_count = turn_count
            self.mover_host = mover_host
            self.mover_port = mover_port
            self.board = board
            super().__init__()

    class WinnerMessage(Message):
        """TUI game winner message"""
        def __init__(self, winner_host, winner_port, board):
            self.winner_host = winner_host
            self.winner_port = winner_port
            self.board = board
            super().__init__()

    class DrawMessage(Message):
        """TUI game draw message"""
        def __init__(self, board):
            self.board = board
            super().__init__()


    def __init__(self, sock, logger) -> None:
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
        button = cast(ColumnButton, event.button)
        self.action_move(button.col)

    def on_game_make_log(self, message: Game.MakeLog) -> None:
        if message.severity == "info":
            self.logger.info(message.line)
        elif message.severity == "debug":
            self.logger.debug(message.line)
        elif message.severity == "error":
            self.logger.error(message.line)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.action_name(event.value)
        self.switch_mode("waiting")

    def on_connect_four_status_message(self, message: StatusMessage) -> None:
        try:
            game = self.query_one(Game)
        except NoMatches:
            self.pop_screen()
            game = self.query_one(Game)
        self.logger.debug("received status message")
        self.turn_count = message.turn_count
        self.board = message.board
        for loc, value in self.board.items():
            game.color_cell(loc[0], loc[1], value)
        self.query_one(GameStatus).who = self.users.get_mover_name(message.mover_host, message.mover_port)

    def on_connect_four_winner_message(self, message: WinnerMessage) -> None:
        try:
            game = self.query_one(Game)
        except NoMatches:
            self.pop_screen()
            game = self.query_one(Game)
        self.logger.info("Game won!, setting finished")
        for button in self.query(ColumnButton):
            button.disabled = True
        self.board = message.board
        for loc, value in self.board.items():
            game.color_cell(loc[0], loc[1], value)
        winner = self.users.get_mover_name(message.winner_host, message.winner_port)
        status = self.query_one(GameStatus)
        status.who = f"{winner}!"
        status.status = "The Winner is: "
        status.exit_msg = "Press 'q' to quit"

    def on_connect_four_draw_message(self, message: DrawMessage) -> None:
        try:
            game = self.query_one(Game)
        except NoMatches:
            self.pop_screen()
            game = self.query_one(Game)
        self.logger.info("Game was a draw, setting finished")
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
        self.logger.info("TUI setting pregame")
        self.switch_mode("pregame")

    def on_connect_four_waiting_message(self, message: WaitingMessage) -> None:
        self.logger.info("TUI setting waiting")
        self.switch_mode("waiting")

    async def on_connect_four_run_message(self, message: RunMessage) -> None:
        self.logger.info("TUI setting run")
        self.users = message.users
        await self.switch_mode("game")
        self.query_one(GameStatus).who = self.users.first.name
        self.board = message.board
        game = self.query_one(Game)
        for loc, value in self.board.items():
            game.color_cell(loc[0], loc[1], value)



    def on_mount(self) -> None:
        self.switch_mode("waiting")

    def action_ping(self) -> None:
        self.sock.sendall(self.action.ping())

    def action_move(self, col: int) -> None:
        self.sock.sendall(self.action.move(col, self.turn_count))

    def action_name(self, name: str) -> None:
        self.sock.sendall(self.action.set_name(name))

