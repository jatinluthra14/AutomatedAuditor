import sys
from models.bucket import Bucket


def print_usage():
    print(f"Usage: python {__file__} <bucket_name>")
    print(f"Example: python {__file__} test_bucket")
    exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        bucket_name = ""
    else:
        bucket_name = sys.argv[1].strip()

    bucket = Bucket(bucket_name=bucket_name)
    bucket.start()
