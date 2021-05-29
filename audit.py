import sys
import boto3
import boto3.session
import threading
from itertools import cycle
from shutil import get_terminal_size
import time

class Bucket():
    def __init__(self, bucket_name: str = "") -> None:
        self.session = boto3.session.Session()
        self.s3 = self.session.client('s3')

        self.bucket_name = bucket_name

        self.loading_done = True
        self.loading_steps = ['|', '/', '-', '\\']

    def validate_bucket(self) -> bool:
        self.load_message('Validating Bucket...')
        if not self.bucket_name:
            return False

        buckets = list[str]()
        for bucket in self.s3.list_buckets()['Buckets']:
            buckets.append(bucket['Name'])
        return self.bucket_name in buckets

    def load_message(self, message) -> None:
        loading_thread = threading.Thread(target=self.loading, args=(message, ), daemon=True)
        self.loading_done = False
        loading_thread.start()

    def done_message(self, message) -> None:
        self.loading_done = True
        time.sleep(0.1)
        cols = get_terminal_size((80, 24)).columns
        print("\r" + " " * cols, end="", flush=True)
        print(f"\r{message}", flush=True)

    def loading(self, message) -> None:
        for step in cycle(self.loading_steps):
            if self.loading_done:
                break
            print(f'\r[{step}] {message}', end="", flush=True)
            time.sleep(0.1)


def print_usage():
    print(f"Usage: python {__file__} <bucket_name>")
    print(f"Example: python {__file__} test_bucket")
    exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()

    bucket_name = sys.argv[1].strip()
    print("Selected Bucket:", bucket_name)

    bucket = Bucket(bucket_name=bucket_name)
    if not bucket.validate_bucket():
        bucket.done_message("Invalid Bucket Requested!")
        exit(1)

    bucket.done_message("Bucket Found!")
