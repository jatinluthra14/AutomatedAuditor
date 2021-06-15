from utils.loader import Loader
from utils.cprint import cprint
from google.cloud import storage


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

    def check_iam(self) -> None:
        print(self.client.get_bucket(self.bucket_name).get_iam_policy().bindings)

    def check_all(self) -> None:
        self.check_iam()

    def check_bucket(self) -> None:
        if self.bucket_name:
            cprint("Selected Bucket:", self.bucket_name, info=True)
            if not self.validate_bucket():
                self.loader.done_message(message="Invalid Bucket Requested!", status=False)
                return
            self.loader.done_message(message="Bucket Found!", status=True)
            self.check_all()

    def start(self) -> None:
        if self.bucket_name:
            self.check_bucket()
        else:
            cprint("No Specific Bucket Name Provided, Auditing All", info=True)
            for bucket in self.client.list_buckets():
                self.bucket_name = bucket.name
                self.check_bucket()
