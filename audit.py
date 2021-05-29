import sys
import boto3
import boto3.session
from botocore.exceptions import ClientError
import threading
from itertools import cycle
from shutil import get_terminal_size
import time
from colorama import Fore, Style, init


init(convert=True)


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

    def check_static_website(self) -> None:
        self.load_message("Checking Static Website Hosting...")
        try:
            print(self.s3.get_bucket_website(Bucket=self.bucket_name))
            self.done_message(message="Static Website Hosting configured.", status=False)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchWebsiteConfiguration':
                self.done_message(message="Static Website Hosting not configured.", status=True)
            else:
                self.done_message(message="Unknown Error " + str(e), status=False)

    def check_server_encyption(self) -> None:
        self.load_message("Checking Server Side Encryption...")
        try:
            print(self.s3.get_bucket_encryption(Bucket=self.bucket_name))
            self.done_message(message="Server Side Encryption configured.", status=True)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                self.done_message(message="Server Side Encryption not configured.", status=False)
            else:
                self.done_message(message="Unknown Error " + str(e), status=False)

    def check_logging(self) -> None:
        self.load_message("Checking Audit Logging...")
        try:
            logging = self.s3.get_bucket_logging(Bucket=self.bucket_name)
            if 'LoggingEnabled' in logging:
                self.done_message(message="Audit Logging configured.", status=True)
            else:
                self.done_message(message="Audit Logging not configured.", status=False)
        except ClientError as e:
            self.done_message(message="Unknown Error " + str(e), status=False)

    def check_versioning_mfa(self) -> None:
        self.load_message("Checking Object Versioning and MFA...")
        try:
            versioning = self.s3.get_bucket_versioning(Bucket=self.bucket_name)
            if 'Status' in versioning:
                if versioning['Status'] == 'Enabled':
                    self.done_message(message="Object Versioning Enabled.", status=True)
                else:
                    self.done_message(message=f"Object Versioning {versioning['Status']}.", status=False)
            else:
                self.done_message(message="Object Versioning not configured.", status=False)
            if 'MFADelete' in versioning:
                if versioning['MFADelete'] == 'Enabled':
                    self.done_message(message="MFA Delete Enabled.", status=True)
                else:
                    self.done_message(message=f"MFA Delete {versioning['MFADelete']}.", status=False)
            else:
                self.done_message(message="MFA Delete not configured.", status=False)
        except ClientError as e:
            self.done_message(message="Unknown Error " + str(e), status=False)

    def check_all(self) -> None:
        self.check_static_website()
        self.check_server_encyption()
        self.check_logging()
        self.check_versioning_mfa()

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


def print_usage():
    print(f"Usage: python {__file__} <bucket_name>")
    print(f"Example: python {__file__} test_bucket")
    exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()

    bucket_name = sys.argv[1].strip()
    print(f"{Style.BRIGHT}{Fore.LIGHTCYAN_EX}[i] Selected Bucket:", bucket_name, Style.RESET_ALL)

    bucket = Bucket(bucket_name=bucket_name)
    if not bucket.validate_bucket():
        bucket.done_message(message="Invalid Bucket Requested!", status=False)
        exit(1)

    bucket.done_message(message="Bucket Found!", status=True)

    bucket.check_all()
