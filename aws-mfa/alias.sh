#!/bin/bash
setToken() {
    ~/mfa.sh $1
    echo "Your creds have been set in your env."
}
alias mfa=setToken