from utils.loader import Loader
from utils.cprint import cprint
from google.cloud import storage
import requests


class GCPBucket():
    def __init__(self, bucket_name: str = "", cred_file_path: str = "") -> None:
        self.credentials = None

        if cred_file_path:
            self.client = storage.Client.from_service_account_json(cred_file_path)
        else:
            self.client = storage.Client()

        self.bucket_name = bucket_name
        self.bucket_permissions = {
            'storage.buckets.create':               'Create new buckets in a project.',
            'storage.buckets.delete':               'Delete buckets.',
            'storage.buckets.get':                  'Read bucket metadata, excluding IAM policies.',
            'storage.buckets.getIamPolicy':         'Read bucket IAM policies.',
            'storage.buckets.list':                 'List buckets in a project. Also read bucket metadata, excluding IAM policies, when listing.',
            'storage.buckets.setIamPolicy':         'Update bucket IAM policies.',
            'storage.buckets.update':               'Update bucket metadata, excluding IAM policies.'
        }
        self.object_permissions = {
            'storage.objects.create':               'Add new objects to a bucket.',
            'storage.objects.delete':               'Delete objects.',
            'storage.objects.get':                  'Read object data and metadata, excluding ACLs.',
            'storage.objects.getIamPolicy':         'Read object ACLs, returned as IAM policies.',
            'storage.objects.list':                 'List objects in a bucket. Also read object metadata, excluding ACLs, when listing.',
            'storage.objects.setIamPolicy':         'Update object ACLs.',
            'storage.objects.update':               'Update object metadata, excluding ACLs.'
        }

        self.loader = Loader()

    def validate_bucket(self) -> bool:
        self.loader.load_message('Validating Bucket...')
        if not self.bucket_name:
            return False

        buckets = list[str]()
        for bucket in self.client.list_buckets():
            buckets.append(bucket.name)
        return self.bucket_name in buckets

    def check_bucket_iam_auth(self) -> None:
        bucket_perms = [perm for perm in self.bucket_permissions.keys() if perm != 'storage.buckets.create' and perm != 'storage.buckets.list']
        self.loader.load_message('Checking for Authenticated Bucket Permissions...')

        bucket_perm_check = self.client.bucket(self.bucket_name).test_iam_permissions(permissions=bucket_perms)
        if bucket_perm_check:
            self.loader.done_message(message='Found Authenticated Bucket Permissions!', status=True)
            cprint('\t' + '\n\t'.join([self.bucket_permissions[key] for key in bucket_perm_check]), info=True, symbol=False)
        else:
            self.loader.done_message(message='No Authenticated Bucket Permissions Found!', status=False)

    def check_object_iam_auth(self) -> None:
        object_perms = [perm for perm in self.object_permissions.keys() if perm != 'storage.objects.getIamPolicy' and perm != 'storage.objects.setIamPolicy']
        self.loader.load_message('Checking for Authenticated Object Permissions...')

        object_perm_check = self.client.bucket(self.bucket_name).test_iam_permissions(permissions=object_perms)
        if object_perm_check:
            self.loader.done_message(message='Found Authenticated Object Permissions!', status=True)
            cprint('\t' + '\n\t'.join([self.object_permissions[key] for key in object_perm_check]), info=True, symbol=False)
        else:
            self.loader.done_message(message='No Authenticated Object Permissions Found!', status=False)

    def check_bucket_iam_unauth(self) -> None:
        bucket_perms = [f'permissions={perm}' for perm in self.bucket_permissions.keys() if perm != 'storage.buckets.create' and perm != 'storage.buckets.list']
        self.loader.load_message('Checking for Unauthenticated Bucket Permissions...')

        bucket_perm_check = requests.get(f'https://www.googleapis.com/storage/v1/b/{self.bucket_name}/iam/testPermissions?{"&".join(bucket_perms)}').json()
        if bucket_perm_check.get('permissions'):
            self.loader.done_message(message='Found Unauthenticated Bucket Permissions!', status=True)
            cprint('\t' + '\n\t'.join([self.bucket_permissions[key] for key in bucket_perm_check['permissions']]), info=True, symbol=False)
        else:
            self.loader.done_message(message='No Unauthenticated Bucket Permissions Found!', status=False)

    def check_object_iam_unauth(self) -> None:
        object_perms = [f'permissions={perm}' for perm in self.object_permissions.keys() if perm != 'storage.objects.getIamPolicy' and perm != 'storage.objects.setIamPolicy']
        self.loader.load_message('Checking for Unauthenticated Object Permissions...')

        object_perm_check = requests.get(f'https://www.googleapis.com/storage/v1/b/{self.bucket_name}/iam/testPermissions?{"&".join(object_perms)}').json()
        if object_perm_check.get('permissions'):
            self.loader.done_message(message='Found Unauthenticated Object Permissions!', status=True)
            cprint('\t' + '\n\t'.join([self.object_permissions[key] for key in object_perm_check['permissions']]), info=True, symbol=False)
        else:
            self.loader.done_message(message='No Unauthenticated Object Permissions Found!', status=False)

    def check_all(self) -> None:
        self.check_bucket_iam_auth()
        self.check_object_iam_auth()
        self.check_bucket_iam_unauth()
        self.check_object_iam_unauth()

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
