from utils.cprint import cprint
from utils.loader import Loader
from azure.identity import ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError
from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import ContainerClient


class AZBlob():
    def __init__(self, container_name: str = "", storage_acct_name: str = "", tenant_id: str = "", client_id: str = "", client_secret: str = "", subscription_id: str = "") -> None:
        self.container_name = container_name
        self.storage_acct_name = storage_acct_name
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.subscription_id = subscription_id

        self.credential: ClientSecretCredential
        self.storage_mgmt: StorageManagementClient
        self.client: ContainerClient
        self.storage_accts = list[str]()

        self.loader = Loader()

    def validate_creds(self) -> bool:
        self.loader.load_message('Validating Credentials...')
        try:
            self.credential = ClientSecretCredential(tenant_id=self.tenant_id, client_id=self.client_id, client_secret=self.client_secret)
            token = self.credential._request_token('https://storage.azure.com/.default')
            if token:
                return True
        except ClientAuthenticationError as e:
            cprint(e, error=True)
        return False

    def check_storage_acct(self) -> bool:
        self.loader.load_message('Validating Storage Account...')
        try:
            self.storage_mgmt = StorageManagementClient(credential=self.credential, subscription_id=self.subscription_id)
            self.storage_accts = [str(storage_acct.name) for storage_acct in self.storage_mgmt.storage_accounts.list()]
            if self.storage_acct_name in self.storage_accts:
                return True
        except Exception as e:
            self.loader.done_message(message=e, status=False)
        return False

    def start(self) -> None:
        if not self.validate_creds():
            self.loader.done_message(message="Error in Credentials.", status=False)
            return
        self.loader.done_message(message="Credentials Validated.", status=True)

        if not self.check_storage_acct():
            self.loader.done_message(message="Invalid Storage Account Requested!", status=False)
            return
        self.loader.done_message(message="Storage Account Validated.", status=True)
