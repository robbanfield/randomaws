import boto3
import botocore.exceptions
import logging
from logging.config import fileConfig
import click

fileConfig('logconfig.ini')
logger = logging.getLogger(__name__)

# Assumed profiles - tweak to my needs
account_options=["developer", "qa", "staging", "sandbox", "production", "root", "all"]
PROFILE_MAPPINGS = {
    "developer": "developer",
    "qa": "qa",
    "staging": "staging",
    "sandbox": "sandbox",
    "production": "prod",
    "root": "root"
}

account_default=account_options[0]

@click.command()
@click.option('--profile', '-p', type=click.Choice(account_options), default=account_default, help="AWS Profile configured to C2P CLI practices. (default developer)")
@click.option('--region', '-r', help='Region to scan')

def main(profile,region):

    if profile == account_options[-1]:
        targets = account_options[0:-1]
    else:
        targets = [profile]

    if region is None:
        session = boto3.session.Session(profile_name="developer", region_name="ca-central-1")
        regions = session.client("ec2").describe_regions(Filters=[{"Name":"opt-in-status", "Values": ['opt-in-not-required','opted-in']}]) ['Regions']
    else:
        regions = [{'RegionName':region}]


    for target in targets:
        logger.info(f"Scanning AWS Account {target} ")
        for region in regions:
            logger.info(f"Scanning {target}::{region['RegionName']}")
            session = boto3.session.Session(profile_name=target, region_name=region['RegionName'])
            ec2_client = session.client("ec2")
            keypairs = ec2_client.describe_key_pairs()
            for key in keypairs['KeyPairs']:
                instances = ec2_client.describe_instances(Filters=[{'Name':"key-name", "Values":[key['KeyName']]}])['Reservations']
                logger.info(f" {key['KeyName']} - {len(instances)}")





if __name__ == '__main__':
    main()
