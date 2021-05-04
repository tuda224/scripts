# AWS multi-factor-authentication
Copy the mfa.cfg, mfa.sh and alias.sh file into your home folder. If you copy it somewhere else adapt the file paths accordingly.

## mfa.cfg
Adapt the config file in a way that it contains your default AWS credentials.
Those values are used on every MFA token generation.

## alias.sh
In your `~/.bashrc` file add the following line:

    source ~/alias.sh

This will ensure that you will always be able to call the script from anywhere.

## How to use
On the command line call the script like:

    mfa [your-mfa-code]

### Be aware
The script overrides the credentials file of AWS CLI (usually located at `~/.aws/credentials`). Which means that any credentials you configured before will be lost.