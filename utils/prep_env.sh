#!/bin/bash

[ -z "$PYTHONVER" ] && PYTHONVER=python3
virt_name=$1
[ -z "$virt_name" ] && virt_name=virt 

CurrentPath=$(dirname "$(readlink -f "$0")")
cd $CurrentPath/../..

grep 'install_requires' */setup.py  | sed 's|.*install_requires=\[||g' | sed 's|\],||g' | sed 's|, |\n|g' | sed 's|"||g' | egrep -v 'lucterios|diacamma' | sort | uniq > requirement.txt
echo "PyCryptodome" >> requirement.txt
echo "pycodestyle" >> requirement.txt
echo "coverage" >> requirement.txt
echo "wheel" >> requirement.txt
echo "Sphinx" >> requirement.txt
echo "mysqlclient" >> requirement.txt
echo "psycopg2-binary" >> requirement.txt

[ -d virt ] && rm -rf $virt_name

python3 -m virtualenv --python=$PYTHONVER $virt_name
[ $? -ne 0 ] && echo "-- virtualenv for $PYTHONVER not create  --" && exit 2

source $virt_name/bin/activate

pip install -U -r requirement.txt

pip list

deactivate
