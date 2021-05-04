#!/bin/bash
#
# call script with one argument which is the mfa code from your mfa device
# 
# Once the temp token is obtained it is set in the credentials file as
# your default profile. This way it can be used by the local backend
#
# script is based on following work:
#   - https://github.com/asagage/aws-mfa-script
#   - https://gist.github.com/ogavrisevs/2debdcb96d3002a9cbf2

# first unset all environment variables and credentials file
unset AWS_SESSION_TOKEN
unset AWS_SECURITY_TOKEN
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
echo "" > ~/.aws/credentials

AWS_CLI=`which aws`

if [ $? -ne 0 ]; then
  echo "AWS CLI is not installed; exiting"
  exit 1
else
  echo "Using AWS CLI found at $AWS_CLI"
fi

# only 1 argument allowed
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <MFA_TOKEN_CODE>"
  echo "Where:"
  echo "   <MFA_TOKEN_CODE> = Code from virtual MFA device"
  exit 2
fi

echo "Reading config..."
if [ ! -r ~/mfa.cfg ]; then
  echo "No config found.  Please create your mfa.cfg.  See README.txt for more info."
  exit 2
fi

MFA_TOKEN_CODE=$1
ARN_OF_MFA=$(grep "^mfa_device" ~/mfa.cfg | cut -d '=' -f2- | tr -d '"')
AWS_ACCESS_KEY_ID=$(grep "^aws_access_key_id" ~/mfa.cfg | cut -d '=' -f2- | tr -d '"')
AWS_SECRET_ACCESS_KEY=$(grep "^aws_secret_access_key" ~/mfa.cfg | cut -d '=' -f2- | tr -d '"')
echo "Access key id in config: $AWS_ACCESS_KEY_ID"
echo "Secret access key in config: $AWS_SECRET_ACCESS_KEY"

# set basic aws authentication as environment variables
# so that they can be used from the aws cli to generate the mfa-session-token
export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

echo "AWS-CLI Profile: $AWS_CLI_PROFILE"
echo "MFA ARN: $ARN_OF_MFA"
echo "MFA Token Code: $MFA_TOKEN_CODE"

read AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN <<< $( aws sts get-session-token --duration 129600 --serial-number $ARN_OF_MFA --token-code $MFA_TOKEN_CODE --output text  | awk '{ print $2, $4, $5 }')

echo "Your credentials:"
echo "AWS_ACCESS_KEY_ID: " $AWS_ACCESS_KEY_ID
echo "AWS_SECRET_ACCESS_KEY: " $AWS_SECRET_ACCESS_KEY
echo "AWS_SESSION_TOKEN: " $AWS_SESSION_TOKEN

# take response and write it into ~.aws/credentials as default profile
echo "[default]" > ~/.aws/credentials
echo "aws_access_key_id = $AWS_ACCESS_KEY_ID" >> ~/.aws/credentials
echo "aws_secret_access_key = $AWS_SECRET_ACCESS_KEY" >> ~/.aws/credentials
echo "aws_session_token = $AWS_SESSION_TOKEN" >> ~/.aws/credentials