import sys


def print_usage():
    print(f"Usage: python {__file__} <bucket_name>")
    print(f"Example: python {__file__} test_bucket")
    exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()

    bucket_name = sys.argv[0].strip()
    print("Selected Bucket:", bucket_name)
