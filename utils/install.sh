#!/usr/bin/env bash

if [ "$(id -u)" != "0" ]; then
   echo ">>> This script must be run as 'super user' <<<" 1>&2
   [ -z "$(which sudo)" ] && exit 1
   sudo -E $0 $@
   sudo chmod -R ogu+w ~/.cache/pip	
   exit $!
fi

EXTRA_URL="http://pypi.lucterios.org/simple"
PACKAGES="lucterios-standard"
ICON_PATH="lucterios/install/lucterios.png"
APP_NAME="Lucterios"

function usage
{
	echo "${0##*/}: installation for Lucterios"
	echo "	${0##*/} -h"
	echo "	${0##*/} [-e <extra_url>] [-p <packages>] [-i <icon_path>] [-n <application_name>]"
	echo "option:"
	echo " -h: show this help"
	echo " -e: define a extra url of pypi server (default: '$EXTRA_URL')"
	echo " -p: define the packages list to install (default: '$PACKAGES')"
	echo " -i: define the icon path for shortcut (default: '$ICON_PATH')"
	echo " -n: define the application name for shortcut (default: '$APP_NAME')"
	exit 0
}

while getopts "e:i:p:n:h" opt ; do
    case $opt in
    e) EXTRA_URL="$OPTARG"
       ;;
    i) ICON_PATH="$OPTARG"
       ;;
    p) PACKAGES="$OPTARG"
       ;;
    n) APP_NAME="$OPTARG"
       ;;
    h) usage $0
       exit 0
       ;;
   \?) echo "Unrecognized parameter -$OPTARG" >&2
       exit 1
       ;;
    :) echo "Option -$OPTARG requires an argument." >&2
       exit 1
       ;;
    esac
done

PIP_OPTION="--extra-index-url $EXTRA_URL --trusted-host $(echo $EXTRA_URL | awk -F/ '{print $3}')"
if [ ! -z "$http_proxy" ]
then
	PIP_OPTION="$PIP_OPTION --proxy=$http_proxy"
fi

echo "====== install lucterios ======"

echo "install: extra_url=$EXTRA_URL packages=$PACKAGES icon_path=$ICON_PATH application_name=$APP_NAME"

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
	brew_perm=`stat -c "%G:%U" $(which brew)`
	chown root:wheel $(which brew)
	brew install libxml2 libxslt
	easy_install pip
	brew install python3
	chown $brew_perm $(which brew)
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

$PIP_CMD install $PIP_OPTION virtualenv -U	

mkdir -p /var/lucterios2
cd /var/lucterios2
$PYTHON_CMD $(which virtualenv) virtual_for_lucterios

echo
echo "------ install lucterios ------"
echo

. /var/lucterios2/virtual_for_lucterios/bin/activate
pip install $PIP_OPTION -U $PACKAGES

echo
echo "------ refresh shortcut ------"
echo
rm -rf /var/lucterios2/launch_lucterios.sh
touch /var/lucterios2/launch_lucterios.sh
echo "#!/usr/bin/env bash" >> /var/lucterios2/launch_lucterios.sh
echo  >> /var/lucterios2/launch_lucterios.sh
echo ". /var/lucterios2/virtual_for_lucterios/bin/activate" >> /var/lucterios2/launch_lucterios.sh
echo "cd /var/lucterios2/" >> /var/lucterios2/launch_lucterios.sh
if [ ! -z "$EXTRA_URL" ]
then
	echo "export extra_url='$EXTRA_URL'" >> /var/lucterios2/launch_lucterios.sh
fi
if [ -z "$LANG" -o "$LANG" == "C" ]
then
	echo "export LANG=en_US.UTF-8" >> /var/lucterios2/launch_lucterios.sh
fi

cp /var/lucterios2/launch_lucterios.sh /var/lucterios2/launch_lucterios_gui.sh
echo "lucterios_gui.py" >> /var/lucterios2/launch_lucterios_gui.sh
chmod +x /var/lucterios2/launch_lucterios_gui.sh

echo 'lucterios_admin.py $@' >> /var/lucterios2/launch_lucterios.sh
chmod +x /var/lucterios2/launch_lucterios.sh
chmod -R ogu+w /var/lucterios2

ln -sf /var/lucterios2/launch_lucterios.sh /usr/local/bin/launch_lucterios
ln -sf /var/lucterios2/launch_lucterios_gui.sh /usr/local/bin/launch_lucterios_gui

if [ -d "/usr/share/applications" ]
then
	LAUNCHER="/usr/share/applications/lucterios.desktop"
	echo "[Desktop Entry]" > $LAUNCHER
	echo "Name=$APP_NAME" >> $LAUNCHER
	echo "Comment=$APP_NAME installer" >> $LAUNCHER
	echo "Exec=/var/lucterios2/launch_lucterios_gui.sh" >> $LAUNCHER
	echo "Icon=/var/lucterios2/virtual_for_lucterios/lib/python3.4/site-packages/$ICON_PATH" >> $LAUNCHER
	echo "Terminal=false" >> $LAUNCHER
	echo "Type=Application" >> $LAUNCHER
	echo "Categories=Office" >> $LAUNCHER
fi
if [ "${OSTYPE:0:6}" == "darwin" ]
then
	APPDIR="/Applications/$APP_NAME.app"
	mkdir -p "$APPDIR/Contents/MacOS"
	cp "/var/lucterios2/launch_lucterios_gui.sh" "$APPDIR/Contents/MacOS/$APP_NAME"
	chmod ogu+rx "$APPDIR/Contents/MacOS/$APP_NAME"
	# change icon
	icon="/var/lucterios2/virtual_for_lucterios/lib/python3.4/site-packages/$ICON_PATH"
	rm -rf $APPDIR$'/Icon\r'
	sips -i $icon >/dev/null
	DeRez -only icns $icon > /tmp/icns.rsrc
	Rez -append /tmp/icns.rsrc -o $APPDIR$'/Icon\r'
	SetFile -a C $APPDIR
	SetFile -a V $APPDIR$'/Icon\r'
	chmod -R ogu+r $APPDIR
fi

echo "============ END ============="
exit 0
