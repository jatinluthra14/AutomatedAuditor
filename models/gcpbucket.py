from google.cloud import storage
from google.oauth2 import service_account


class GCPBucket():
    def __init__(self, bucket_name: str = "", cred_file_path: str = "") -> None:
        self.credentials = None

        if cred_file_path:
            self.credentials = service_account.Credentials.from_service_account_file(cred_file_path)

        self.client = storage.Client(project=None, credentials=self.credentials)
