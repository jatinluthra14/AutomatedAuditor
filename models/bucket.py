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
    def __init__(self, bucket_name: str = "", aws_access_key_id: str = "", aws_secret_access_key: str = "") -> None:
        if aws_access_key_id and aws_secret_access_key:
            self.session = boto3.session.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        else:
            self.session = boto3.session.Session()

        self.s3 = self.session.client('s3')

        self.bucket_name = bucket_name

        self.loading_done = True
        self.loading_steps = ['|', '/', '-', '\\']

        self.bucket_acl_map = {
            "READ": "%s can List Objects in the Bucket",
            "WRITE": "%s can Create, Modify and Delete Objects in the Bucket",
            "READ_ACP": "%s can Read Bucket ACL",
            "WRITE_ACP": "%s can Modify the Bucket ACL",
            "FULL_CONTROL": "%s has Full Control on the Bucket"
        }

    def validate_creds(self) -> bool:
        sts = self.session.client('sts')
        try:
            ident = sts.get_caller_identity()
            if not ident:
                return False
            else:
                return True
        except ClientError as e:
            print(f"{Style.BRIGHT}{Fore.LIGHTRED_EX} [-]", e.response['Error']['Code'], Style.RESET_ALL)
            return False

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
            self.s3.get_bucket_website(Bucket=self.bucket_name)
            self.done_message(message="Static Website Hosting configured.", status=False)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchWebsiteConfiguration':
                self.done_message(message="Static Website Hosting not configured.", status=True)
            else:
                self.done_message(message="Unknown Error " + str(e), status=False)

    def check_server_encyption(self) -> None:
        self.load_message("Checking Server Side Encryption...")
        try:
            self.s3.get_bucket_encryption(Bucket=self.bucket_name)
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

    def check_bucket_acl(self) -> None:
        self.load_message("Checking Bucket ACL...")
        status = True
        try:
            bucket_acl = self.s3.get_bucket_acl(Bucket=self.bucket_name)
            if 'Grants' in bucket_acl:
                for grant in bucket_acl['Grants']:
                    grantee = grant['Grantee']
                    permission = grant['Permission']
                    if grantee['Type'] == 'Group':
                        group = grantee['URI'].split('/')[-1]
                        if group == "AuthenticatedUsers" or group == "AllUsers":
                            status = False
                            self.done_message(message=self.bucket_acl_map[permission] % group, status=status)
                if status:
                    self.done_message(message="Bucket ACLs configured properly.", status=True)
            else:
                self.done_message(message="Bucket ACL not configured.", status=False)
        except ClientError as e:
            self.done_message(message="Unknown Error " + str(e), status=False)

    def check_all(self) -> None:
        self.check_static_website()
        self.check_server_encyption()
        self.check_logging()
        self.check_versioning_mfa()
        self.check_bucket_acl()

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

    def check_bucket(self) -> None:
        if self.bucket_name:
            print(f"{Style.BRIGHT}{Fore.LIGHTCYAN_EX}[i] Selected Bucket:", self.bucket_name, Style.RESET_ALL)
            if not self.validate_bucket():
                self.done_message(message="Invalid Bucket Requested!", status=False)
                return
            self.done_message(message="Bucket Found!", status=True)
            self.check_all()

    def start(self) -> None:
        if not self.validate_creds():
            print(f"{Style.BRIGHT}{Fore.LIGHTRED_EX} [-] Error in Credentials", Style.RESET_ALL)
            return

        if self.bucket_name:
            self.check_bucket()
        else:
            print(f"{Style.BRIGHT}{Fore.LIGHTCYAN_EX}[i] No Specific Bucket Name Provided, Auditing All", Style.RESET_ALL)
            for bucket in self.s3.list_buckets()['Buckets']:
                self.bucket_name = bucket['Name']
                self.check_bucket()
