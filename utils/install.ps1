#requires -version 4.0
#requires -runasadministrator

echo "====== install lucterios ======"

echo
echo "------ download python -------"
echo

$url = "https://www.python.org/ftp/python/3.4.3/python-3.4.3.amd64.msi"
$python_install = "$env:temp\python.msi"
$webclient = New-Object System.Net.WebClient
$webclient.DownloadFile($url,$python_install)

$url = "https://raw.github.com/pypa/pip/master/contrib/get-pip.py"
$pip_install = "$env:temp\get-pip.py"
$webclient = New-Object System.Net.WebClient
$webclient.DownloadFile($url,$pip_install)

echo
echo "------ install python -------"
echo

msiexec /i $python_install /qn
python $pip_install
pip install virtualenv

echo
echo "------ configure virtual environment ------"
echo

mkdir -p c:/lucterios2
cd c:/lucterios2
python virtualenv virtual_for_lucterios

echo
echo "------ install lucterios ------"
echo

c:/lucterios2/virtual_for_lucterios/Scripts/activate
pip install --extra-index-url http://v2.lucterios.org/simple --trusted-host v2.lucterios.org -U lucterios-standard

echo
echo "------ refresh shortcut ------"
echo


echo "============ END ============="
exit 0

