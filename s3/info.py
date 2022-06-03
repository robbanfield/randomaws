from re import T
import boto3
import botocore.exceptions
import logging
from logging.config import fileConfig
import click

fileConfig('logconfig.ini')
logger = logging.getLogger(__name__)

account_options=[ "root", "all"]
PROFILE_MAPPINGS = {
    "root": "root"
}

account_default=account_options[0]

def get_cfn_stack(client,bucket):

    try:
        cfn_stack=""
        tags = client.get_bucket_tagging(Bucket=bucket['Name'])['TagSet']
        for tag in tags:
            if tag['Key'] == "aws:cloudformation:stack-name" :
                cfn_stack=tag['Value']
                break

        if cfn_stack == "":
            logger.debug("- CFN: NIL Bucket appears manually created")
        else:
            logger.debug(f"- CFN: {cfn_stack}")
        return cfn_stack
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == "NoSuchTagSet":
            logger.debug(f"- No Tags detected")
            logger.debug("- CFN: NIL")
        else:
            logger.error(error)
        return "N/A"


def get_encrypted(s3_client,bucket):
    try:
        enc_status = s3_client.get_bucket_encryption(Bucket=bucket['Name'])
        algo = enc_status['ServerSideEncryptionConfiguration']['Rules'][0]['ApplyServerSideEncryptionByDefault']['SSEAlgorithm']
        logger.debug(f"- Algo: {algo}")
        return algo
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == "ServerSideEncryptionConfigurationNotFoundError":
            logger.debug(f"- No Server Side Encryption config found.")

        else:
            logger.error(error)
        return "N/A"

def get_logging(s3_client,bucket):

    try:
        logging_status = s3_client.get_bucket_logging(Bucket=bucket['Name'])
        if 'LoggingEnabled' in logging_status:
            logging.debug(f"- Logging Enabled - OMG: {logging_status['LoggingEnabled']['TargetBucket']}")
            return logging_status['LoggingEnabled']['TargetBucket']
        else:
            logging.debug(f"- No Logging enabled")

    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == "ServerSideEncryptionConfigurationNotFoundError":
            logger.debug(f"- No Server Side Encryption config found.")
        else:
            logger.error(error)
        return "N/A"

def get_meta(s3_client,bucket):
    try:
        response = s3_client.list_objects_v2(Bucket= bucket['Name'])
        if "Contents" in response:
            logger.debug(len(response['Contents']))
            return len(response['Contents'])
        else:
            logger.debug (" - No Contents")
            return 0
    except botocore.exceptions.ClientError as error:
        logger.error(f"{bucket['Name']} query error - {error.response['Error']['Code']}")

def get_policy(s3_client,bucket):
    try:
        return s3_client.get_bucket_policy(Bucket=bucket['Name'])
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == "NoSuchBucketPolicy":
            logger.debug(f"- No Bucket Policy")
        else:
            logger.error(error)
        return ""




@click.command()
@click.option('--profile', '-p', type=click.Choice(account_options), default=account_default, help="AWS Profile configured to C2P CLI practices. (default developer)")
def main(profile):

    if profile == account_options[-1]:
        targets = account_options[0:-1]
    else:
        targets = [profile]

    logger.info(f"Scanning: {targets} ")

    for target in targets:
        logger.info(f"Scanning AWS Account {target}")
        session = boto3.session.Session(profile_name=target, region_name="ca-central-1")
        s3_client = session.client("s3")
        for bucket in s3_client.list_buckets()['Buckets']:
            logger.debug(f"{bucket['Name']}")
            logger.debug(f"- Created {bucket['CreationDate']}")



            encrypt = get_encrypted(s3_client,bucket)
            if encrypt == "N/A":
                account_suffix=PROFILE_MAPPINGS[target]
                stack= get_cfn_stack(s3_client,bucket)
                count = get_meta(s3_client,bucket)
                log_bucket= get_logging(s3_client,bucket)


                policy = get_policy(s3_client, bucket)
                logger.warning(f"{ticket:9}>> {bucket['Name']} {bucket['CreationDate']} => Stack: {stack},  encrypt: {encrypt}, log_bucket: {log_bucket}, count={count}")
            else:
                logger.debug(f"{bucket['Name']} - OK")

if __name__ == '__main__':
    main()
