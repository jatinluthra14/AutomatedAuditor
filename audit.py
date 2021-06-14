import sys
from models.s3bucket import S3Bucket
from getpass import getpass

platforms = ['aws', 'gcp']


def print_usage():
    print(f"Usage: python {__file__} <platform(aws|gcp)> <bucket_name>")
    print(f"Example: python {__file__} aws test_bucket")
    exit(1)


def input_creds() -> tuple[str, str]:
    inp = input("Would you like to manually provide AWS credentials (No if it is saved in config file) Y/[N]: ").strip().upper()
    if not inp:
        inp = "N"

    if inp == "Y":
        aws_access_key_id = input("Enter AWS Access Key ID: ").strip()
        aws_secret_access_key = getpass(prompt="Enter AWS Secret Access Key (Input will be hidden): ").strip()
        return (aws_access_key_id, aws_secret_access_key)
    else:
        return ("", "")


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

    creds = input_creds()
    if creds[0] and creds[1]:
        bucket = S3Bucket(bucket_name=bucket_name, aws_access_key_id=creds[0], aws_secret_access_key=creds[1])
    else:
        bucket = S3Bucket(bucket_name=bucket_name)
    bucket.start()
