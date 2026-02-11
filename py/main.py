import threading
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Label, Input, Static
from textual.containers import Container, Vertical, Horizontal, Center, Middle
from textual.screen import ModalScreen
from textual.binding import Binding

from scraper import run_scraper
from utils import create_smart_button
import sys

if sys.platform == "win32":
    # \x1b[8;H;Wt  (H=Lines, W=Columns)
    sys.stdout.write("\x1b[8;16;108t")
    sys.stdout.flush()
class LinkInputScreen(ModalScreen):
    BINDINGS = [("escape", "close_dialog", "Schließen")]

    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                with Vertical(id="modal-dialog"):
                    yield Label("🔗 Link eingeben:", id="modal-title")
                    yield Input(placeholder="URL hier einfügen...", id="link-field")
                    with Horizontal(id="modal-buttons"):
                        yield Button("Abbrechen", variant="error", id="cancel_btn")
                        yield Button("Scrapen", variant="success", id="ok_btn")

    def on_mount(self):
        self.query_one("#link-field").focus()

    def action_close_dialog(self):
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "ok_btn":
            self.process_link()
        elif event.button.id == "cancel_btn":
            self.app.pop_screen()

    def on_input_submitted(self, event: Input.Submitted):
        self.process_link()

    def process_link(self):
        input_widget = self.query_one("#link-field", Input)
        link = input_widget.value.strip()
        if link:
            self.notify(f"Scrape gestartet...", title="MOTILITY")
            threading.Thread(target=run_scraper, args=(link,), daemon=True).start()
            input_widget.value = ""
        input_widget.focus()

class MotilityApp(App):
    TITLE = "MOTILITY"
    
    MIN_WIDTH = 108 
    MIN_HEIGHT = 16 

    BINDINGS = [
        Binding("q", "quit", "Beenden"),
        Binding("left", "prev_page", "Vorherige Seite", show=False),
        Binding("right", "next_page", "Nächste Seite", show=False),
        Binding("escape", "quit", "Beenden", show=False),
    ]

    CSS = """
    #button-grid {
        layout: grid;
        grid-size: 3;
        grid-columns: 1fr 1fr 1fr;
        /* Wir lassen grid-rows auf auto, damit nur der gutter zählt */
        grid-rows: auto; 
        /* EXAKT 2 Zeilen vertikaler Abstand zwischen Reihen */
        grid-gutter: 2 2; 
        align: center middle;
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    
    #button-grid Button { 
        width: 35; 
        height: 5; 
    }

    #page-indicator {
        width: 100%;
        text-align: center;
        color: $accent;
        text-style: bold;
        /* EXAKT 2 Zeilen Abstand zur untersten Button-Reihe */
        margin-top: 2; 
        margin-bottom: 1;
    }

    #modal-dialog {
        width: 70;
        height: auto;
        border: panel $primary;
        background: $surface;
        padding: 1 2;
    }

    #modal-title { width: 100%; text-align: center; margin-bottom: 1; }
    #link-field { margin-bottom: 1; }
    #modal-buttons { width: 100%; height: 3; content-align: center middle; margin-bottom: 1; }
    #modal-buttons Button { margin: 0 1; width: 25; }

    #size-warning {
        display: none; 
        background: $error 90%; 
        color: white;
        text-align: center; 
        text-style: bold; 
        layer: top;
        height: 100%; 
        width: 100%; 
        content-align: center middle;
    }
    #size-warning.visible { display: block; }
    """

    def __init__(self):
        super().__init__()
        self.shortcuts = {}
        self.current_page = 0
        self.all_buttons_data = [
            ("&Api-Shop Scrapen", "api_scrape")
        ]
        self.max_per_page = 6

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("", id="size-warning")
        with Vertical():
            with Container(id="button-grid"):
                pass 
            yield Static("", id="page-indicator")
        yield Footer()

    def on_mount(self):
        self.update_page()

    def update_page(self):
        grid = self.query_one("#button-grid")
        grid.query("Button").remove()
        self.shortcuts = {}

        start = self.current_page * self.max_per_page
        end = start + self.max_per_page
        page_items = self.all_buttons_data[start:end]

        for text, btn_id in page_items:
            grid.mount(create_smart_button(text, btn_id, self.shortcuts))
        
        total_pages = (len(self.all_buttons_data) - 1) // self.max_per_page + 1
        self.query_one("#page-indicator").update(f"Seite {self.current_page + 1} von {total_pages} (← / →)")

    def action_next_page(self):
        if (self.current_page + 1) * self.max_per_page < len(self.all_buttons_data):
            self.current_page += 1
            self.update_page()

    def action_prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page()

    def on_key(self, event):
        if len(self.screen_stack) == 1:
            key = event.key.lower()
            if key in self.shortcuts:
                self.handle_action(self.shortcuts[key])

    def handle_action(self, action_id: str):
        if action_id == "exit":
            self.exit()
        elif action_id == "api_scrape":
            self.push_screen(LinkInputScreen())

    def on_button_pressed(self, event: Button.Pressed):
        self.handle_action(event.button.id)

    def on_resize(self, event):
        warning = self.query_one("#size-warning", Static)
        diff_w = self.MIN_WIDTH - event.size.width
        diff_h = self.MIN_HEIGHT - event.size.height
        if diff_w > 0 or diff_h > 0:
            warning.update(f"⚠️ ZU KLEIN ⚠️\n\nB: +{max(0, diff_w)} H: +{max(0, diff_h)}")
            warning.add_class("visible")
        else:
            warning.remove_class("visible")

if __name__ == "__main__":
    MotilityApp().run()
