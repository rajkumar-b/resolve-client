#!/bin/bash

echo "Checking prerequisities..."

if [ -z "$LAMBDA_PYTHON_HOME" ]; then
    echo "Environment var LAMBDA_PYTHON_HOME is undefined/empty"
    exit 1
fi

VIRTUAL_ENV_BIN=$LAMBDA_PYTHON_HOME/bin/virtualenv
if [ ! -f $VIRTUAL_ENV_BIN ]; then
    echo "Couldn't find virtualenv $VIRTUAL_ENV_BIN. Please install it using pip."
    exit 1
fi

export SUB_PROJECT="resolve-client"            # subproject inside repository
LAMBDA_HOME="$PWD"			                       # local system lambda build directory
LAMBDA_PYTHON_VER="3.6"                        # runtime python version for lambda
LAMBDA_PYTHON_BIN="$LAMBDA_PYTHON_HOME/bin/python$LAMBDA_PYTHON_VER"
PYTHON_BIN=$LAMBDA_PYTHON_BIN                  # local python used to build+upload lambda zip

if [ ! -f $LAMBDA_PYTHON_BIN ]; then
    echo "Couldn't find correct python binary for lambda - $LAMBDA_PYTHON_BIN"
    exit 1
fi

$PYTHON_BIN -c "import boto3"
if [ $? -ne 0 ]; then
    echo "Couldn't find boto3 for python $LAMBDA_PYTHON_BIN. Please install it"
    exit 1
fi
#######END PREREQUISITES###############


REPO_LOCATION=$HOME/Resolve_Client
ZIP_LOCATION=$REPO_LOCATION
ENV_LOCATION=$REPO_LOCATION/.envs
STAGING_LOCATION=$REPO_LOCATION/.staging
LOG_LOCATION=/tmp/lambda-logs
for loc in $ZIP_LOCATION $ENV_LOCATION $STAGING_LOCATION $LOG_LOCATION; do
    if [ ! -d $loc ]; then
        mkdir -p $loc || { echo "failed to create $loc"; exit 1; }
    fi
done

LOG_FILE=$LOG_LOCATION/$(date +"%Y-%m-%d-%s").log
echo "Will use log file: $LOG_FILE"
cd $REPO_LOCATION

LAMBDA_REQUIREMENTS=$LAMBDA_HOME/requirements.txt
if [ -f $LAMBDA_REQUIREMENTS ]; then
    LAMBDA_PYENV=$ENV_LOCATION/${SUB_PROJECT}_env
    rm -r $LAMBDA_PYENV
    if [ ! -d $LAMBDA_PYENV ]; then
        echo "Creating virtualenv - $LAMBDA_PYENV"
        $VIRTUAL_ENV_BIN -p $LAMBDA_PYTHON_BIN $LAMBDA_PYENV || exit 1 &>> $LOG_FILE
    else
        echo "Env directory not deleted" && exit 1
    fi
    echo "Installing requirements."
    source $LAMBDA_PYENV/bin/activate
    pip install -r $LAMBDA_REQUIREMENTS &>> $LOG_FILE
    deactivate
else
    echo "No requirements.txt. No dependencies to import."
fi

echo "Clearing staging dir."
LAMBDA_STAGING=$STAGING_LOCATION/${SUB_PROJECT}
rm -rf $LAMBDA_STAGING
mkdir -p $LAMBDA_STAGING
echo "Copying project files." # Boto is already available in lambda env
if [ ! -z "$LAMBDA_PYENV" ]; then
    rsync -a $LAMBDA_PYENV/lib/python$LAMBDA_PYTHON_VER/site-packages/. $LAMBDA_STAGING/ \
    --exclude pip --exclude 'boto*' --exclude setuptools --exclude docutils || exit 1
fi
rsync -a $LAMBDA_HOME/. $LAMBDA_STAGING/ || exit 1
echo "Files copied into staging"


echo "Generating zip"
cd $LAMBDA_STAGING
export LAMBDA_ZIP=$ZIP_LOCATION/${SUB_PROJECT}.zip
zip -FSqr $LAMBDA_ZIP * -x \*.txt &>> $LOG_FILE

PID=$(pgrep zip)
while ps -o pid -ax | grep -qs $PID ; do
  sleep 1
done
echo "Zip created - $LAMBDA_ZIP"

unset LAMBDA_ZIP


