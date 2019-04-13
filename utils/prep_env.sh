#!/bin/bash

CurrentPath=$(dirname "$(readlink -f "$0")")
cd $CurrentPath/../..

grep 'install_requires' */setup.py  | sed 's|.*install_requires=\[||g' | sed 's|\],||g' | sed 's|, |\n|g' | sed 's|"||g' | egrep -v 'lucterios|diacamma' | sort | uniq > requirement.txt
echo "pycodestyle" >> requirement.txt
echo "coverage" >> requirement.txt
echo "wheel" >> requirement.txt
echo "Sphinx" >> requirement.txt
echo "mysqlclient" >> requirement.txt
echo "psycopg2" >> requirement.txt

[ -d virt ] && rm -rf virt

python3 $(which virtualenv) virt

source virt/bin/activate

pip install -U -r requirement.txt

pip list

deactivate