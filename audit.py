import sys
from models.s3bucket import S3Bucket
from models.gcpbucket import GCPBucket
from getpass import getpass

platforms = ['aws', 'gcp']


def print_usage() -> None:
    print(f"Usage: python {__file__} <platform(aws|gcp)> <bucket_name>")
    print(f"Example: python {__file__} aws test_bucket")
    exit(1)


def init_s3bucket(bucket_name: str = "") -> None:
    inp = input("Would you like to manually provide AWS credentials (No if it is saved in config file) Y/[N]: ").strip().upper()
    if not inp:
        inp = "N"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    if inp == "Y":
        aws_access_key_id = input("Enter AWS Access Key ID: ").strip()
        aws_secret_access_key = getpass(prompt="Enter AWS Secret Access Key (Input will be hidden): ").strip()

    if aws_access_key_id and aws_secret_access_key:
        bucket = S3Bucket(bucket_name=bucket_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    else:
        bucket = S3Bucket(bucket_name=bucket_name)
    bucket.start()


def init_gcpbucket(bucket_name: str = "") -> None:
    inp = input("Would you like to manually provide GCP credentials (No if it is saved in config file) Y/[N]: ").strip().upper()
    if not inp:
        inp = "N"
    cred_file_path: str = ""
    if inp == "Y":
        cred_file_path = input("Enter GCP Credentials JSON File Path: ").strip()

    bucket = GCPBucket(bucket_name=bucket_name, cred_file_path=cred_file_path)
    bucket.start()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Error: Less Number of Arguments!")
        print_usage()
    elif len(sys.argv) < 3:
        bucket_name = ""
    else:
        bucket_name = sys.argv[2].strip()

    platform = sys.argv[1].lower().strip()
    if platform not in platforms:
        print("Error: Invalid Platform!")
        print_usage()

    if platform == 'aws':
        init_s3bucket(bucket_name)
    elif platform == 'gcp':
        init_gcpbucket(bucket_name)
