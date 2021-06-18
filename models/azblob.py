from typing import Any
from utils.cprint import cprint
from utils.loader import Loader
from azure.identity import ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError
from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import ContainerClient, BlobServiceClient


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
        self.bs_client: BlobServiceClient
        self.client: ContainerClient
        self.blob = ''
        self.storage_acct_properties = dict[str, Any]()
        self.storage_containers = list[str]()
        self.container_properties = dict[str, Any]()

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

    def validate_container(self) -> bool:
        self.loader.load_message('Validating Container...')
        try:
            if len(self.storage_containers) < 1:
                self.storage_containers = [str(container.name) for container in self.bs_client.list_containers()]
            if self.container_name in self.storage_containers:
                return True
        except Exception as e:
            cprint(e, error=True)
            pass
        return False

    def check_storage_acct(self) -> bool:
        self.loader.load_message('Validating Storage Account...')
        try:
            self.storage_mgmt = StorageManagementClient(credential=self.credential, subscription_id=self.subscription_id)
            for storage_acct in self.storage_mgmt.storage_accounts.list():
                if str(storage_acct.name) == self.storage_acct_name:
                    self.storage_acct_properties = storage_acct.as_dict()
                    self.blob = str(storage_acct.primary_endpoints.blob)
                    self.bs_client = BlobServiceClient(account_url=self.blob, credential=self.credential)
                    return True
        except Exception as e:
            self.loader.done_message(message=e, status=False)
        return False

    def check_container(self) -> None:
        if self.container_name:
            cprint(self.container_name, info=True)
            if not self.validate_container():
                self.loader.done_message(message="Invalid Container Requested!", status=False)
                return
            self.loader.done_message(message="Container Found!", status=True)
            self.client = ContainerClient(account_url=self.blob, container_name=self.container_name, credential=self.credential)
            self.container_properties = self.client.get_container_properties().__dict__
            self.check_all_container()

    def check_secure_transfer(self) -> None:
        self.loader.load_message("Checking Secure Transfer...")
        if 'enable_https_traffic_only' in self.storage_acct_properties:
            if self.storage_acct_properties['enable_https_traffic_only']:
                self.loader.done_message(message="Secure Transfer enabled.", status=True)
                return

        self.loader.done_message(message="Secure Transfer disabled.", status=False)

    def check_shared_key_access(self) -> None:
        self.loader.load_message("Checking Shared Key Access...")
        if 'allow_shared_key_access' in self.storage_acct_properties:
            if self.storage_acct_properties['allow_shared_key_access']:
                self.loader.done_message(message="Shared Key Access enabled.", status=False)
                return

        self.loader.done_message(message="Shared Key Access disabled.", status=True)

    def check_firewall_rules(self) -> None:
        self.loader.load_message("Checking Firewall Rules...")
        if 'network_rule_set' in self.storage_acct_properties:
            if 'ip_rules' in self.storage_acct_properties['network_rule_set']:
                if self.storage_acct_properties['network_rule_set']['ip_rules']:
                    self.loader.done_message(message="Firewall Rules enabled.", status=True)
                    return

        self.loader.done_message(message="Firewall Rules disabled.", status=False)

    def check_limit_network_access(self) -> None:
        self.loader.load_message("Checking if Network Access is Limited...")
        if 'network_rule_set' in self.storage_acct_properties:
            if 'default_action' in self.storage_acct_properties['network_rule_set']:
                if self.storage_acct_properties['network_rule_set']['default_action'] == 'Allow':
                    self.loader.done_message(message="Network Access not limited.", status=False)
                    return

        self.loader.done_message(message="Network Access not limited.", status=True)

    def check_customer_managed_keys(self) -> None:
        self.loader.load_message("Checking Customer Managed Keys...")
        if 'encryption' in self.storage_acct_properties:
            if 'key_vault_properties' in self.storage_acct_properties['encryption']:
                if self.storage_acct_properties['encryption']['key_vault_properties']:
                    self.loader.done_message(message="Customer Managed Keys enabled.", status=True)
                    return

        self.loader.done_message(message="Customer Managed Keys disabled.", status=False)

    def check_public_access_storage_acct(self) -> None:
        self.loader.load_message("Checking Public Access on Storage Account...")
        if 'allow_blob_public_access' in self.storage_acct_properties:
            if self.storage_acct_properties['allow_blob_public_access']:
                self.loader.done_message(message="Public Access is enabled on the complete storage account.", status=False)
                return

        self.loader.done_message(message="Public Access disabled.", status=True)

    def check_public_access_container(self) -> None:
        self.loader.load_message("Checking Public Access on Container...")
        if 'public_access' in self.container_properties:
            if self.container_properties['public_access'] == 'container':
                self.loader.done_message(message="Public Access is enabled on the container.", status=False)
                return

        self.loader.done_message(message="Public Access disabled.", status=True)

    def check_immutable_policy(self) -> None:
        self.loader.load_message("Checking Immutability Policy...")
        if 'has_immutability_policy' in self.container_properties:
            if not self.container_properties['has_immutability_policy']:
                self.loader.done_message(message="No Immutability Policy on the container.", status=False)
                return

        self.loader.done_message(message="Immutability Policy enabled.", status=True)

    def check_all_storage_acct(self) -> None:
        self.check_secure_transfer()
        self.check_shared_key_access()
        self.check_firewall_rules()
        self.check_limit_network_access()
        self.check_customer_managed_keys()
        self.check_public_access_storage_acct()

    def check_all_container(self) -> None:
        self.check_public_access_container()
        self.check_immutable_policy()

    def start(self) -> None:
        if not self.validate_creds():
            self.loader.done_message(message="Error in Credentials.", status=False)
            return
        self.loader.done_message(message="Credentials Validated.", status=True)

        if not self.check_storage_acct():
            self.loader.done_message(message="Invalid Storage Account Requested!", status=False)
            return
        self.loader.done_message(message="Storage Account Validated.", status=True)

        cprint('Performing Security Checks on the Storage Account!', info=True)
        self.check_all_storage_acct()

        cprint('Performing Security Checks on the Container!', info=True)
        if self.container_name:
            self.check_container()
        else:
            cprint("No Specific Container Name Provided, Auditing All", info=True)
            for container in self.bs_client.list_containers():
                self.container_name = container.name
                self.check_container()
