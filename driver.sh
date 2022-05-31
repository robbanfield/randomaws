if [[ "$0" == "$1" ]]; then
    echo "No inception here"
    exit 1
fi

if [ "$2" != "" ]; then
    profiles=$2
else
    profiles=$(aws configure list-profiles | grep -v -e default )
fi

mkdir -p ./output/$1

for profile in ${profiles[@]}
do

    echo "Profile $profile"
    # leverage default
    for region in $(aws ec2 describe-regions --region us-east-1 --profile default  --query "Regions[].{Name:RegionName}" --output text)
    do
        echo "Checking $profile:$region"
        bash $1 $region $profile | tee output/$1/$profile-$region
    done
done%   
