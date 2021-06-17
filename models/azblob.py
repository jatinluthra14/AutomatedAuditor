from azure.identity import ClientSecretCredential


class AZBlob():
    def __init__(self, container_name: str = "", tenant_id: str = "", client_id: str = "", client_secret: str = "", subscription_id: str = "") -> None:
        self.container_name = container_name
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.subscription_id = subscription_id

        self.credential = ClientSecretCredential(tenant_id=self.tenant_id, client_id=self.client_id, client_secret=self.client_secret)
