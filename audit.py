import sys
import boto3
import boto3.session


class Bucket():
    def __init__(self, bucket_name: str = "") -> None:
        self.session = boto3.session.Session()
        self.s3 = self.session.client('s3')

        self.bucket_name = bucket_name

    def validate_bucket(self) -> bool:
        if not self.bucket_name:
            return False

        buckets = list[str]()
        for bucket in self.s3.list_buckets()['Buckets']:
            buckets.append(bucket['Name'])
        return self.bucket_name in buckets


def print_usage():
    print(f"Usage: python {__file__} <bucket_name>")
    print(f"Example: python {__file__} test_bucket")
    exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()

    bucket_name = sys.argv[1].strip()
    print("Selected Bucket:", bucket_name)

    bucket = Bucket(bucket_name=bucket_name)
    if not bucket.validate_bucket():
        print("Invalid Bucket Requested!")
        exit(1)

    print("Bucket Found!")
