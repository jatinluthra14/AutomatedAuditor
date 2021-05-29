import sys
from models.bucket import Bucket
from colorama import Fore, Style, init

init(convert=True)


def print_usage():
    print(f"Usage: python {__file__} <bucket_name>")
    print(f"Example: python {__file__} test_bucket")
    exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()

    bucket_name = sys.argv[1].strip()
    print(f"{Style.BRIGHT}{Fore.LIGHTCYAN_EX}[i] Selected Bucket:", bucket_name, Style.RESET_ALL)

    bucket = Bucket(bucket_name=bucket_name)
    if not bucket.validate_bucket():
        bucket.done_message(message="Invalid Bucket Requested!", status=False)
        exit(1)

    bucket.done_message(message="Bucket Found!", status=True)

    bucket.check_all()
