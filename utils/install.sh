#!/usr/bin/env bash

if [ "$(id -u)" != "0" ]; then
   echo ">>> This script must be run as 'super user' <<<" 1>&2
   [ -z "$(which sudo)" ] && exit 1
   sudo -E $0 $@	
   exit $!
fi

if [ "$1" = "del" ]
then
	echo "====== delete lucterios ======"
	rm -f /usr/local/bin/launch_lucterios
	rm -f /usr/local/bin/launch_lucterios_gui
	rm -rf /var/lucterios2/
	echo "============ END ============="
	exit 0
fi

if [ ! -z "$1" ]
then
	echo "${0##*/}: installation for Lucterios"
	echo "option:"
	echo "	${0##*/} help			This help"
	echo "	${0##*/} del			Remove Lucterios"
	exit 0
fi

echo "====== install lucterios ======"

echo
echo "------ check perquisite -------"
echo

if [ ! -z "$(which apt-get)" ]; then  # DEB linux like
	apt-get install -y libxml2-dev libxslt-dev libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev
	apt-get install -y python-pip python-dev
	apt-get install -y python3-pip python3-dev
	apt-get install -y python-tk python-imaging
	apt-get install -y python3-tk python3-imaging
else if [ ! -z "$(which yum)" ]; then # RPM unix/linux like
	yum install -y python-devel libxml2-devel libxslt-devel libjpeg-devel
	yum install -y libfreetype6 libfreetype6-devel
	yum install -y tkinter 
	yum install -y python-imaging	
	easy_install pip
else if [ ! -z "$(which brew)" ]; then # Mac OS X
	brew install libxml2 libxslt
	easy_install pip
	brew install python3
	pip3 install --upgrade pip
else
	echo "++++++ Unix/Linux distribution not available for this script! +++++++"
fi; fi; fi

echo
echo "------ configure virtual environment ------"
echo

PIP_CMD=
PYTHON_CMD=
for pip_iter in 3 2
do
	 if [ -z "$PIP_CMD" -a ! -z "$(which "pip$pip_iter")" ]
	 then
	 	PIP_CMD="pip$pip_iter"
	 	PYTHON_CMD="python$pip_iter"
	 fi 
done
[ -z "$PIP_CMD" ] && echo "No pip found!" && exit 1

set -e

PIP_OPTION=''
if [ ! -z "$http_proxy" ]
then
	PIP_OPTION="--proxy=$http_proxy"
fi
$PIP_CMD install $PIP_OPTION virtualenv -U	

mkdir -p /var/lucterios2
cd /var/lucterios2
$PYTHON_CMD $(which virtualenv) virtual_for_lucterios

echo
echo "------ install lucterios ------"
echo

. /var/lucterios2/virtual_for_lucterios/bin/activate
pip install $PIP_OPTION --extra-index-url http://v2.lucterios.org/simple --trusted-host v2.lucterios.org -U lucterios-standard

echo
echo "------ refresh shortcut ------"
echo
rm -rf /var/lucterios2/launch_lucterios.sh
touch /var/lucterios2/launch_lucterios.sh
echo "#!/usr/bin/env bash" >> /var/lucterios2/launch_lucterios.sh
echo  >> /var/lucterios2/launch_lucterios.sh
echo ". /var/lucterios2/virtual_for_lucterios/bin/activate" >> /var/lucterios2/launch_lucterios.sh
echo "cd /var/lucterios2/" >> /var/lucterios2/launch_lucterios.sh
echo "export extra_url='http://v2.lucterios.org/simple'" >> /var/lucterios2/launch_lucterios.sh
if [ -z "$LANG" -o "$LANG" == "C" ]
then
	echo "export LANG=en_US.UTF-8" >> /var/lucterios2/launch_lucterios.sh
fi
rm -rf /var/lucterios2/launch_lucterios.sh
touch /var/lucterios2/launch_lucterios.sh
echo "#!/bin/sh" >> /var/lucterios2/launch_lucterios.sh
echo  >> /var/lucterios2/launch_lucterios.sh
echo ". /var/lucterios2/virtual_for_lucterios/bin/activate" >> /var/lucterios2/launch_lucterios.sh
echo "cd /var/lucterios2/" >> /var/lucterios2/launch_lucterios.sh
cp /var/lucterios2/launch_lucterios.sh /var/lucterios2/launch_lucterios_gui.sh
echo "lucterios_gui.py" >> /var/lucterios2/launch_lucterios_gui.sh
chmod +x /var/lucterios2/launch_lucterios_gui.sh

echo 'lucterios_admin.py $@' >> /var/lucterios2/launch_lucterios.sh
chmod +x /var/lucterios2/launch_lucterios.sh
chmod ogu+w /var/lucterios2

ln -sf /var/lucterios2/launch_lucterios.sh /usr/local/bin/launch_lucterios
ln -sf /var/lucterios2/launch_lucterios_gui.sh /usr/local/bin/launch_lucterios_gui

if [ -d "/usr/share/applications" ]
then
	LAUNCHER="/usr/share/applications/lucterios.desktop"
	echo "[Desktop Entry]" > $LAUNCHER
	echo "Name=Lucterios" >> $LAUNCHER
	echo "Comment=Lucterios installer" >> $LAUNCHER
	echo "Exec=/var/lucterios2/launch_lucterios_gui.sh" >> $LAUNCHER
	echo "Icon=/var/lucterios2/virtual_for_lucterios/lib/python3.4/site-packages/lucterios/install/lucterios.png" >> $LAUNCHER
	echo "Terminal=false" >> $LAUNCHER
	echo "Type=Application" >> $LAUNCHER
	echo "Categories=Office" >> $LAUNCHER
fi
if [ "${OSTYPE:0:6}" == "darwin" ]
then
	app_dir="/application/Lucterios.app"	
	mkdir -p "$app_dir/Contents/MacOS"
	cp "/var/lucterios2/launch_lucterios_gui.sh" "$app_dir/Lucterios"
	chmod +x "$app_dir/Contents/MacOS/Lucterios"
	# change icon
	icon="/var/lucterios2/virtual_for_lucterios/lib/python3.4/site-packages/lucterios/install/lucterios.png"
	rm -rf $app_dir$'/Icon\r'
	sips -i $icon >/dev/null
	DeRez -only icns $icon > /tmp/icns.rsrc
	Rez -append /tmp/icns.rsrc -o $app_dir$'/Icon\r'
	SetFile -a C $app_dir
	SetFile -a V $app_dir$'/Icon\r'
	chmod ogu+r $app_dir
fi

echo "============ END ============="
exit 0
