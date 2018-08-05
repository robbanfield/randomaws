# Assuming Python 2.7 / MAC
import click
import boto3


def processInstance(instance, type, forceResize, ec2):

    instanceId = instance['InstanceId']
    print("Process Instance {} - current instance type {}".format(instance['InstanceId'], instance['InstanceType']))
    if type == instance['InstanceType']:
        print("Instance is already listed as a {} ".format(type))
    else:
        confirmation = "F"
        if not forceResize:
            confirmation = raw_input("Confirm resize of this instance: Y to process, all other fail: ")
        if forceResize or "Y" == confirmation:
            print ("Resize Initiated")
            print ("- Stopping")
            ec2.stop_instances(InstanceIds=[instanceId])
            waiter = ec2.get_waiter('instance_stopped')
            print ("- Waiting for instance to stop")
            waiter.wait(InstanceIds=[instanceId])
            print ("- Issue Resize command")
            ec2.modify_instance_attribute(InstanceId=instanceId, Attribute='instanceType', Value=type)
            print ("- Initiate Restart")
            ec2.start_instances(InstanceIds=[instanceId])
        else:
            print ("Aborting")


@click.command()
@click.option("--account", '-a', prompt="Account", help="Boto label for the AWS account")
@click.option("--region", '-r', prompt="AWS Region", help="Region is the instance in")
@click.option("--instance", '-i', prompt="Instance ID", help="Instance ID to resize")
@click.option('--type', '-t', prompt="New Instance Type", help="New instance type")
@click.option('--force/--no-force', '-F',  default=False, help="Non-Interactive - do not prompt for confirmation")
def main(account, region, instance, type, force):
    """
    :param region: Region to locate instance
    :param account: Boto3 Label of the account in environment. https://boto3.readthedocs.io/en/latest/guide/configuration.html
    :param instance: Instance Id to resize
    :param type: New instance size
    :param force: Force the resize
    """
    print ("Validating Instance {} in Account {}, region {} ".format( instance, account, region))
    try:
        filters= [{'Name': 'instance-id', 'Values': [instance]}]
        ec2 = boto3.session.Session(profile_name=account, region_name=region).client('ec2')
        ec2Instance=ec2.describe_instances(Filters=filters)['Reservations']
        # Restrict to just 1, for now.
        if len(ec2Instance) == 1:
            processInstance(ec2Instance[0]['Instances'][0], type, force, ec2)
        else:
            print ("Unable to continue")

    except Exception as e:
        print("Error Processing \n\t{}".format(e.message))

if __name__ == '__main__':
    main()
