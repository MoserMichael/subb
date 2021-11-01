#!/bin/bash

set -e 

rm -rf tst || true
mkdir tst
pushd tst
# test installation of module in virtual environment
virtualenv my-venv
source my-venv/bin/activate

pip3 install subb 
cp ../*.py .
python3 ./test.py

echo "everything is fine. test passed"

deactivate

#rm -rf my-venv

popd tst
