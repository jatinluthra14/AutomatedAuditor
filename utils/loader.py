import threading
from itertools import cycle
from shutil import get_terminal_size
import time
from colorama import Fore, Style, init

init(convert=True)


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
        color = Fore.LIGHTRED_EX + '[-] ' if not status else Fore.LIGHTGREEN_EX + '[+] '
        cols = get_terminal_size((80, 24)).columns
        print("\r" + " " * cols, end="", flush=True)
        print(f"\r{Style.BRIGHT}{color}{message}{Style.RESET_ALL}", flush=True)

    def loading(self, message) -> None:
        for step in cycle(self.loading_steps):
            if self.loading_done:
                break
            print(f'\r{Style.BRIGHT}{Fore.LIGHTBLUE_EX}[{step}] {message}{Style.RESET_ALL}', end="", flush=True)
            time.sleep(0.1)
