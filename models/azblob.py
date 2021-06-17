from azure.identity import ClientSecretCredential
from utils.cprint import cprint
from azure.core.exceptions import ClientAuthenticationError


class AZBlob():
    def __init__(self, container_name: str = "", tenant_id: str = "", client_id: str = "", client_secret: str = "", subscription_id: str = "") -> None:
        self.container_name = container_name
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.subscription_id = subscription_id

        self.credential: ClientSecretCredential

    def validate_creds(self) -> bool:
        try:
            self.credential = ClientSecretCredential(tenant_id=self.tenant_id, client_id=self.client_id, client_secret=self.client_secret)
            token = self.credential._request_token('https://storage.azure.com/.default')
            print(token)
            if token:
                return True
        except ClientAuthenticationError as e:
            cprint(e, error=True)
        return False

    def start(self) -> None:
        if not self.validate_creds():
            cprint("Error in Credentials", error=True)
            return
