set -ex
virtualenv env
source env/bin/activate
pip3.7 install google-cloud-storage
pip3.7 install audioread
