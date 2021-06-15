from models.s3bucket import S3Bucket
from models.gcpbucket import GCPBucket
import argparse

platforms = ['aws', 'gcp']


def init_s3bucket(args: argparse.Namespace) -> None:
    if args.aws_creds:
        bucket = S3Bucket(bucket_name=args.bucket_name, aws_access_key_id=args.aws_creds[0], aws_secret_access_key=args.aws_creds[1])
    else:
        bucket = S3Bucket(bucket_name=args.bucket_name)
    bucket.start()


def init_gcpbucket(args: argparse.Namespace) -> None:
    bucket = GCPBucket(bucket_name=args.bucket_name, cred_file_path=args.gcp_creds)
    bucket.start()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='A Cross Cloud Platform Automated Auditor')
    parser.add_argument('platform', help='The Platform you want to audit', choices=platforms, type=str.lower)
    parser.add_argument('-b', '--bucket-name', default='', metavar='BucketName', help='The Name of Bucket to Audit (Exclude to Audit All)')
    parser.add_argument('--aws-creds', default='', nargs=2, metavar=('AWS_Access_Key_ID', 'AWS_Secret_Access_Key'), help='AWS ID and Secret key (Space Separated)')
    parser.add_argument('--gcp-creds', default='', metavar='JSON_Path', help='GCP Creds JSON File Path')
    args = parser.parse_args()

    if args.platform == 'aws':
        init_s3bucket(args)
    elif args.platform == 'gcp':
        init_gcpbucket(args)
