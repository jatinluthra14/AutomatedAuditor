from models.s3bucket import S3Bucket
from models.gcpbucket import GCPBucket
from models.azblob import AZBlob
from utils.cprint import cprint
import argparse
import json
import os

platforms = ['aws', 'gcp', 'az']


def read_creds(file_path: str = "") -> dict[str, str]:
    creds = dict[str, str]()
    try:
        creds = json.loads(open(file_path, 'r').read())
    except json.JSONDecodeError:
        cprint("Invalid JSON File (Match the format with --gen-config)", error=True)
    except FileNotFoundError:
        cprint("Invalid File Path (Enclose in double quotes if path contains spaces)", error=True)
    return creds


def init_s3bucket(args: argparse.Namespace) -> None:
    if args.aws_creds_path:
        creds = read_creds(file_path=args.aws_creds_path)
        if creds and all(key in creds for key in ['access_key_id', 'secret_access_key']):
            bucket = S3Bucket(bucket_name=args.bucket_name, aws_access_key_id=creds['access_key_id'], aws_secret_access_key=creds['secret_access_key'])
        else:
            cprint('Invalid Credential Keys in JSON File', error=True)
            return
    elif args.aws_creds:
        bucket = S3Bucket(bucket_name=args.bucket_name, aws_access_key_id=args.aws_creds[0], aws_secret_access_key=args.aws_creds[1])
    else:
        bucket = S3Bucket(bucket_name=args.bucket_name)
    bucket.start()


def init_gcpbucket(args: argparse.Namespace) -> None:
    if args.gcp_creds:
        bucket = GCPBucket(bucket_name=args.bucket_name, cred_file_path=args.gcp_creds)
    else:
        cprint("No GCP Credentials Specified!", error=True)
        return
    bucket.start()


def init_azblob(args: argparse.Namespace) -> None:
    if args.az_creds_path:
        creds = read_creds(file_path=args.az_creds_path)
        if creds and all(key in creds for key in ['tenant_id', 'client_id', 'client_secret', 'subscription_id']):
            blob = AZBlob(container_name=args.bucket_name, storage_acct_name=args.storage_acct_name, tenant_id=creds['tenant_id'], client_id=creds['client_id'], client_secret=creds['client_secret'], subscription_id=creds['subscription_id'])
        else:
            cprint('Invalid Credential Keys in JSON File', error=True)
            return
    elif args.az_creds:
        blob = AZBlob(container_name=args.bucket_name, storage_acct_name=args.storage_acct_name, tenant_id=args.az_creds[0], client_id=args.az_creds[1], client_secret=args.az_creds[2], subscription_id=args.az_creds[3])
    else:
        cprint("No Azure Credentials Specified!", error=True)
        return
    blob.start()


def gen_config(args: argparse.Namespace) -> None:
    cprint('Generating Config...', info=True)
    platform: str = args.platform
    template: dict[str, str] = json.loads(open(f'templates/{platform}_config.json', 'r').read())

    if platform == 'aws' and args.aws_creds:
        template['access_key_id'] = args.aws_creds[0]
        template['secret_access_key'] = args.aws_creds[1]
    elif platform == 'az' and args.az_creds:
        template['tenant_id'] = args.az_creds[0]
        template['client_id'] = args.az_creds[1]
        template['client_secret'] = args.az_creds[2]
        template['subscription_id'] = args.az_creds[3]
    else:
        cprint(f'Enter the Following Information for {platform.upper()} Platform', info=True)
        for key in template.keys():
            prompt = key.replace('_', ' ').capitalize()
            val = input(prompt + ": ")
            template[key] = val

    fpath = os.path.abspath(f'{platform}_config.json')
    with open(fpath, 'w') as fp:
        fp.write(json.dumps(template))
        cprint("File Written at Path: " + fpath, success=True)
        cprint("Use this file next time to authenticate", info=True)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='A Cross Cloud Platform Automated Auditor')
    parser.add_argument('platform', help='The Platform you want to audit', choices=platforms, type=str.lower)
    parser.add_argument('-b', '--bucket-name', default='', metavar='BucketName', help='The Name of Bucket/Container to Audit (Exclude to Audit All)')
    parser.add_argument('-s', '--storage-acct-name', default='', metavar='StorageAcctName', help='The Name of Storage Account to Audit (Azure Only, Specify Container using -b if needed)')
    parser.add_argument('--aws-creds', default='', nargs=2, metavar=('AWS_Access_Key_ID', 'AWS_Secret_Access_Key'), help='AWS ID and Secret key (Space Separated)')
    parser.add_argument('--gcp-creds', '--gcp-creds-path', default='', metavar='JSON_Path', help='GCP Creds JSON File Path')
    parser.add_argument('--az-creds', default='', nargs=4, metavar=('AZ_Tenant_ID', 'AZ_Client_ID', 'AZ_Client_Secret', 'AZ_Subcription_ID'), help='Azure Service Principal Credentials and an Active Subcription ID (Space Separated)')
    parser.add_argument('--aws-creds-path', default='', metavar='JSON_Path', help='AWS Creds JSON File Path')
    parser.add_argument('--az-creds-path', default='', metavar='JSON_Path', help='Azure Creds JSON File Path')
    parser.add_argument('--gen-config', '-gc', action='store_true', help='Generate a config file for the platform for later use. Pass the values as arguments or enter interactively.')
    args = parser.parse_args()

    if args.gen_config:
        gen_config(args=args)
        exit(0)

    if args.platform == 'aws':
        init_s3bucket(args)
    elif args.platform == 'gcp':
        init_gcpbucket(args)
    elif args.platform == 'az':
        init_azblob(args)
