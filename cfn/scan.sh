if [ "$1" == "" ]; then
    profile="developer"
else
    profile="$1"
fi
rm $profile.txt
for stack in $(aws cloudformation list-stacks --profile $profile --query 'StackSummaries[].StackName' --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE --output text)
do
    if [[ "$stack" == awseb* ]]; then
        echo "Skipping EB Stack" | tee -a $profile.txt
    else
        echo "$stack" | tee -a $profile.txt
        aws cloudformation list-stack-resources --stack-name $stack --profile $profile --query "StackResourceSummaries[].{ID:PhysicalResourceId, Type:ResourceType}" --output table --no-cli-pager | tee -a $profile.txt
    fi
done
