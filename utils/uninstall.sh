#!/usr/bin/env bash

if [ "$(id -u)" != "0" ]; then
   echo ">>> This script must be run as 'super user' <<<" 1>&2
   [ -z "$(which sudo)" ] && exit 1
   sudo -E $0 $@
   exit $!
fi

if [ -z "$APP_NAME" ]
then
	APP_NAME="Lucterios"
fi 

echo "====== delete lucterios ======"
rm -f /usr/local/bin/launch_lucterios
rm -f /usr/local/bin/launch_lucterios_gui
rm -rf /var/lucterios2/
rm -rf /usr/share/applications/lucterios.desktop
rm -rf /Applications/$APP_NAME.app
echo "============ END ============="
exit 0
