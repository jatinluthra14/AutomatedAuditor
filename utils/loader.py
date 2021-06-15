from utils.cprint import cprint
import threading
from itertools import cycle
from shutil import get_terminal_size
import time


class Loader():
    def __init__(self) -> None:
        self.loading_done = True
        self.loading_steps = ['|', '/', '-', '\\']

    def load_message(self, message) -> None:
        loading_thread = threading.Thread(target=self.loading, args=(message, ), daemon=True)
        self.loading_done = False
        loading_thread.start()

    def done_message(self, message: str = "", status: bool = True) -> None:
        self.loading_done = True
        time.sleep(0.1)
        success = status
        error = not status
        cols = get_terminal_size((80, 24)).columns
        cprint(" " * cols, end="", flush=True, carriage=True)
        cprint(f"{message}", success=success, error=error, flush=True, carriage=True)

    def loading(self, message) -> None:
        for step in cycle(self.loading_steps):
            if self.loading_done:
                break
            cprint(f'[{step}]', message, symbol=False, info=True, end="", flush=True, carriage=True)
            time.sleep(0.1)
