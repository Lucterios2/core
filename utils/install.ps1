#requires -version 2.0

function Test-Admin {
  $currentUser = New-Object Security.Principal.WindowsPrincipal $([Security.Principal.WindowsIdentity]::GetCurrent())
  $currentUser.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}

if ((Test-Admin) -eq $false)  {
    Start-Process powershell.exe -Verb RunAs -ArgumentList ('-executionpolicy Bypass -noprofile -noexit -file "{0}" -elevated' -f ($myinvocation.MyCommand.Definition))
    exit
}

echo "====== install lucterios ======"

$lucterios_path="c:\lucterios2"
if ($env:PROCESSOR_ARCHITECTURE -eq "AMD64") {
    $url_python = "https://www.python.org/ftp/python/3.4.3/python-3.4.3.amd64.msi"    
    $url_lxml = "https://raw.githubusercontent.com/Lucterios2/core/master/packages/lxml-3.4.4-cp34-none-win_amd64.whl"
    $url_pycrypto = "https://raw.githubusercontent.com/Lucterios2/core/master/packages/pycrypto-2.6.1-cp34-none-win_amd64.whl"
    $lxml_install = "$env:temp\lxml-3.4.4-cp34-none-win_amd64.whl"
    $pycrypto_install = "$env:temp\pycrypto-2.6.1-cp34-none-win_amd64.whl"
} else {
    $url_python = "https://www.python.org/ftp/python/3.4.3/python-3.4.3.msi"
    $url_lxml = "https://raw.githubusercontent.com/Lucterios2/core/master/packages/lxml-3.4.4-cp34-none-win32.whl"
    $url_pycrypto = "https://raw.githubusercontent.com/Lucterios2/core/master/packages/pycrypto-2.6.1-cp34-none-win32.whl"
    $lxml_install = "$env:temp\lxml-3.4.4-cp34-none-win32.whl"
    $pycrypto_install = "$env:temp\pycrypto-2.6.1-cp34-none-win32.whl"
}
$python_install = "$env:temp\python.msi"

Import-Module BitsTransfer

if (!(Test-Path "c:\Python34")) {

    echo ""
    echo "------ download python -------"
    echo ""

    Start-BitsTransfer -Source $url_python -Destination $python_install
    if (!(Test-Path $python_install)) {
        echo "**** Dowload python failed! *****"
        exit 1
    }echo ""
    echo "------ install python -------"
    echo ""

    msiexec /i $python_install /passive | Out-Null
}

echo ""
echo "------ download and install python tools -------"
echo ""

Start-BitsTransfer -Source $url_lxml -Destination $lxml_install
if (!(Test-Path $lxml_install)) {
    echo "**** Dowload lxml failed! *****"
    exit 1
}

Start-BitsTransfer -Source $url_pycrypto -Destination $pycrypto_install
if (!(Test-Path $pycrypto_install)) {
    echo "**** Dowload pycrypto failed! *****"
    exit 1
}

$env:Path="$env:Path;c:\Python34;c:\Python34\Scripts\"
pip install -U virtualenv

echo ""
echo "------ configure virtual environment ------"
echo ""

if (!(Test-Path $lucterios_path)) {
    mkdir $lucterios_path
}
cd $lucterios_path
virtualenv virtual_for_lucterios

if (!(Test-Path $lucterios_path\virtual_for_lucterios\Scripts\activate)) {
    echo "**** Virtual-Env not created! *****"
    exit 1
}

echo ""
echo "------ install lucterios ------"
echo ""

.\virtual_for_lucterios\Scripts\activate
pip install -U $lxml_install $pycrypto_install
pip install --extra-index-url http://pypi.lucterios.org/simple --trusted-host pypi.lucterios.org -U lucterios-standard

echo ""
echo "------ refresh shortcut ------"
echo ""

if (Test-Path $lucterios_path\launch_lucterios.ps1) {
    del $lucterios_path\launch_lucterios.ps1
}
echo "#requires -version 4.0" >> $lucterios_path\launch_lucterios.ps1
echo "" >> $lucterios_path\launch_lucterios.ps1
echo "echo 'Lucterios GUI launcher'" >> $lucterios_path\launch_lucterios.ps1
echo "" >> $lucterios_path\launch_lucterios.ps1
echo "cd $lucterios_path" >> $lucterios_path\launch_lucterios.ps1
echo "virtual_for_lucterios\Scripts\activate" >> $lucterios_path\launch_lucterios.ps1
echo "" >> $lucterios_path\launch_lucterios.ps1
echo "`$env:Path=`"`$env:Path;c:\Python34;c:\Python34\DLLs`"" >> $lucterios_path\launch_lucterios.ps1
echo "`$env:TCL_LIBRARY='c:\Python34\tcl\tcl8.6'" >> $lucterios_path\launch_lucterios.ps1
echo "`$env:TK_LIBRARY='c:\Python34\tcl\tcl8.6'" >> $lucterios_path\launch_lucterios.ps1
echo "`$env:extra_url='http://pypi.lucterios.org/simple'" >> $lucterios_path\launch_lucterios.ps1
echo "python virtual_for_lucterios\Scripts\lucterios_gui.py" >> $lucterios_path\launch_lucterios.ps1
echo "exit" >> $lucterios_path\launch_lucterios.ps1
echo "" >> $lucterios_path\launch_lucterios.ps1

if (Test-Path $env:Public\Desktop\Lucterios.lnk) {
    del $env:Public\Desktop\Lucterios.lnk
}

$WshShell = New-Object -ComObject WScript.shell
$Shortcut = $WshShell.CreateShortcut("$env:Public\Desktop\Lucterios.lnk")
$Shortcut.TargetPath = "PowerShell.exe"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -File $lucterios_path\launch_lucterios.ps1"
$Shortcut.IconLocation = "$lucterios_path\virtual_for_lucterios\Lib\site-packages\lucterios\install\lucterios.ico"
$Shortcut.WindowStyle = 7
$Shortcut.Save()

echo ""
echo "------ permission ------"
echo ""

$Folders = Get-childItem "$lucterios_path"
$InheritanceFlag = [System.Security.AccessControl.InheritanceFlags]::ContainerInherit -bor [System.Security.AccessControl.InheritanceFlags]::ObjectInherit
$PropagationFlag = [System.Security.AccessControl.PropagationFlags]::None
$objType = [System.Security.AccessControl.AccessControlType]::Allow 

$acl = Get-Acl $Folder
$permission = "domain\user", "Modify", $InheritanceFlag, $PropagationFlag, $objType
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule $permission
$acl.SetAccessRule($accessRule)
Set-Acl $Folder $acl

echo "============ END ============="
exit 0
