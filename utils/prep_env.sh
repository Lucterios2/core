#!/bin/bash

function debian_install
{
    apt-get update
    apt-get upgrade -y
    apt-get autoremove -y
    apt-get install -y --fix-missing
    apt-get install -y build-essential libxml2-dev libxml2 libxslt1-dev libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev  
    apt-get install -y latexmk texlive texlive-latex-extra texlive-lang-french
    apt-get install -y sqlite3 git sphinx libopenjp2-tools gettext
    apt-get install -y locales wget zip
    sed -i 's/^.*\(en_US.UTF-8\)/\1/' /etc/locale.gen
    sed -i 's/^.*\(fr_FR.UTF-8\)/\1/' /etc/locale.gen
    locale-gen    
}

function debian_advanced
{
	apt-get install -y postgresql-9.4 postgresql-server-dev-9.4 postgresql-contrib-9.4
	apt-get install -y mariadb-server mariadb-client
	apt-get install -y npm node-gyp nodejs-dev libssl1.0-dev
	apt-get install -y libopenjp2-tools rpm winehq-stable 
	npm install -g cordova
}

function ant_install
{
    apt-get install -y ant
    mkdir -p /usr/share/java/lib
    wget http://www.java2s.com/Code/JarDownload/ant-contrib/ant-contrib-0.6.jar.zip
    unzip ant-contrib-0.6.jar.zip
    mv ant-contrib-0.6.jar /usr/share/java/lib/ant-contrib-0.6.jar
    rm -f ant-contrib-0.6.jar.zip    
}

function create_requirement
{
    if [ -f setup.py ]
    then
      SETUP_PATH=setup.py
    else
      SETUP_PATH=*/setup.py
    fi
    grep 'install_requires' $SETUP_PATH  | sed 's|.*install_requires=\[||g' | sed 's|\],||g' | sed 's|, |\n|g' | sed 's|"||g' | sort | uniq > requirement.txt
    echo "PyCryptodome" >> requirement.txt
    echo "pycodestyle" >> requirement.txt
    echo "coverage" >> requirement.txt
    echo "radon" >> requirement.txt
    echo "flake8_polyfill" >> requirement.txt
    echo "wheel" >> requirement.txt
    echo "Sphinx" >> requirement.txt
    echo "psycopg2-binary" >> requirement.txt
    echo "anybadge" >> requirement.txt
    
	CurrentPath=$(dirname "$(readlink -f "$0")")    
    echo """
from xml.dom.minidom import parse
import glob
failures=0
errors=0
tests=0
for junit in glob.glob('./junit_*.xml'):
	dom=parse(junit)
	failures+=int(dom.documentElement.getAttribute('failures'))
	errors+=int(dom.documentElement.getAttribute('errors'))
	tests+=int(dom.documentElement.getAttribute('tests'))
print(int(100-(failures+errors)/tests))
""" > $CurrentPath/extract_unit.py
}

function main
{
	(
	    [ -z "$PYTHONVER" ] && PYTHONVER=python3
	    virt_name=$1
	    [ -z "$virt_name" ] && virt_name=virt 
	    CurrentPath=$(dirname "$(readlink -f "$0")")
	    cd $CurrentPath/../..
	    [ -d $virt_name ] && rm -rf $virt_name
	    python3 -m virtualenv --python=$PYTHONVER $virt_name
	    [ $? -ne 0 ] && echo "-- virtualenv for $PYTHONVER not create  --" && exit 2
	    
	    create_requirement
	    
	    source $virt_name/bin/activate
	    sed '/lucterios/d' requirement.txt
	    sed '/diacamma/d' requirement.txt
	    pip install -U -r requirement.txt
	    pip install -U mysqlclient || echo 'mysql problem !'
	    pip list
	    deactivate
    )
}

if [ "$1" == "debian" ]
then
    debian_install
    exit 0
fi

if [ "$1" == "advanced" ]
then
	debian_advanced
    exit 0
fi

if [ "$1" == "ant" ]
then
    ant_install
    exit 0
fi

if [ "$1" == "requirement" ]
then
    create_requirement
    exit 0
fi

main $1
