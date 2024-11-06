from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, Input, Label, Static



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

    BINDINGS = [
            Binding("l, escape", "exit_modal", "Exit Logs")
            ]

    class LogMessage(Static):

        BORDER_TITLE = "Logs"
        BORDER_SUBTITLE = "Press Esc or l to exit"

        def compose(self) -> ComposeResult:
            yield Static("logs")

    def compose(self) -> ComposeResult:
        # yield Static("logs", id="logmodal")
        yield self.LogMessage(id="logmodal")

    def action_exit_modal(self) -> None:
        self.app.pop_screen()


class Game(Screen):

    ROWS = 6
    COLUMNS = 7

    BINDINGS = [
            Binding("left", "navigate(-1)", "Move Left", False),
            Binding("right", "navigate(1)", "Move Right", False),
            Binding("q", "app.quit", "Quit"),
            Binding("l", "logs", "Open/Close Logs")
            ]

    def compose(self) -> ComposeResult:
        """Compose the game screen"""
        # yield GameHeader()
        yield Header()
        # yield Placeholder()
        yield GameRun()
        yield Footer()

    def action_logs(self) -> None:
        self.app.push_screen(LogModal())

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

class ColumnButton(Button):
    """Select button for column to play at"""

    @staticmethod
    def at(col: int) -> str:
        """Returns the ID of the button at given location"""
        return f"colbutton-{col}"

    def __init__(self, col: int) -> None:
        super().__init__(f"{col}", id=self.at(col))


class ConnectFour(App):
    TITLE = "Connect Four"
    CSS_PATH = "./styles/styles.css"
    MODES = {
            "waiting": Waiting,
            "pregame": Pregame,
            "game": Game,
            }

    def __init__(self) -> None:
        super().__init__()

    def on_mount(self) -> None:
        self.switch_mode("pregame")

if __name__ == "__main__":
    ConnectFour().run()
