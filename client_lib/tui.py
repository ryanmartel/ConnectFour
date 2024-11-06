import logging
from typing import cast
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, Input, Label, Log, Static

from client_lib.action import Action
from client_lib.message_handler import MessageHandler

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
                Label("Connected!", id="connected"),
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

    def on_input_submitted(self) -> None:
        self.app.switch_mode("game")

        

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

        def __init__(self, line: str) -> None:
            self.line = line
            super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the game screen"""
        # yield GameHeader()
        yield Header()
        # yield Placeholder()
        yield GameRun()
        yield Footer()

    def column_button(self, col: int) -> ColumnButton:
        """Get the button at this location"""
        return self.query_one(f"#{ColumnButton.at(col)}", ColumnButton)



    def action_logs(self) -> None:
        self.app.push_screen(LogModal())

    def action_navigate(self, column: int) -> None:
        """Navigate to column indicator by offset"""
        self.post_message(self.MakeLog(f"Move at {column}"))
        if isinstance(self.focused, ColumnButton):
            self.set_focus(self.column_button((self.focused.col + column) % self.COLUMNS))

class GameHeader(Widget):
    """Header for the game"""
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(self.app.title, id="app-title")
    
class GameRun(Widget):

    def compose(self) -> ComposeResult:
        yield Static("One", classes="box")
        yield GameGrid()
        # yield Static("Two", classes="box")
        yield ButtonGrid()


class GameGrid(Widget):
    """Main playable grid of cells"""
    def compose(self) -> ComposeResult:
        for row in range(Game.ROWS):
            for column in range(Game.COLUMNS):
                yield Cell(row, column)
                # yield Static(f"{row}-{column}", classes="gridbox")

class Cell(Static):
    """Playable spaces in the game board"""

    @staticmethod
    def at(row: int, col: int) -> str:
        """Returns the ID of the button at given location"""
        return f"colbutton-{col}-{row}"

    def __init__(self, row: int, col: int) -> None:
        super().__init__("", id=self.at(row, col))

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
    turn_count = reactive(0)

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
        print(message.line)
        logs = LogModal.logs
        logs.append(message.line)

    def on_mount(self) -> None:
        self.switch_mode("pregame")

    def action_ping(self) -> None:
        self.sock.sendall(self.action.ping())

    def action_move(self, col: int) -> None:
        self.sock.sendall(self.action.move(col, self.turn_count))

    def action_name(self, name: str) -> None:
        self.sock.sendall(self.action.set_name(name))
