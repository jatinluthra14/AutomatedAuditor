from google.cloud import storage
import threading
from itertools import cycle
from shutil import get_terminal_size
import time
from colorama import Fore, Style, init

init(convert=True)


class GCPBucket():
    def __init__(self, bucket_name: str = "", cred_file_path: str = "") -> None:
        self.credentials = None

        if cred_file_path:
            self.client = storage.Client.from_service_account_json(cred_file_path)
        else:
            self.client = storage.Client()

        self.bucket_name = bucket_name

        self.loading_done = True
        self.loading_steps = ['|', '/', '-', '\\']

    def validate_bucket(self) -> bool:
        self.load_message('Validating Bucket...')
        if not self.bucket_name:
            return False

        buckets = list[str]()
        for bucket in self.client.list_buckets():
            buckets.append(bucket.name)
        return self.bucket_name in buckets

    def check_bucket(self) -> None:
        if self.bucket_name:
            print(f"{Style.BRIGHT}{Fore.LIGHTCYAN_EX}[i] Selected Bucket:", self.bucket_name, Style.RESET_ALL)
            if not self.validate_bucket():
                self.done_message(message="Invalid Bucket Requested!", status=False)
                return
            self.done_message(message="Bucket Found!", status=True)

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

    def start(self) -> None:

        if self.bucket_name:
            self.check_bucket()
        else:
            print(f"{Style.BRIGHT}{Fore.LIGHTCYAN_EX}[i] No Specific Bucket Name Provided, Auditing All", Style.RESET_ALL)
            for bucket in self.client.list_buckets():
                self.bucket_name = bucket.name
                self.check_bucket()
