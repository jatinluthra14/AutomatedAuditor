from utils.loader import Loader
from google.cloud import storage
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

        self.loader = Loader()

    def validate_bucket(self) -> bool:
        self.loader.load_message('Validating Bucket...')
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
                self.loader.done_message(message="Invalid Bucket Requested!", status=False)
                return
            self.loader.done_message(message="Bucket Found!", status=True)

    def start(self) -> None:

        if self.bucket_name:
            self.check_bucket()
        else:
            print(f"{Style.BRIGHT}{Fore.LIGHTCYAN_EX}[i] No Specific Bucket Name Provided, Auditing All", Style.RESET_ALL)
            for bucket in self.client.list_buckets():
                self.bucket_name = bucket.name
                self.check_bucket()
