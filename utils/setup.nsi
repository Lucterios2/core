; Lucterios2.nsi
;

;--------------------------------

!include "MUI2.nsh"

!define TEMP $R0
!define TEMP2 $R1

; The name of the installer
Name "Lucterios"

BrandingText "www.sd-libre.fr - Sdl 2015"

; The file to write
OutFile "..\bin\lucterios_setup.exe"

; The default installation directory
InstallDir c:\Lucterios2

WindowIcon on
Icon ..\utils\favicon.ico
UninstallIcon ..\utils\favicon.ico

; Registry key to check for directory (so if you install again, it will 
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\Lucterios2" "Install_Dir"

; Request application privileges for Windows Vista
RequestExecutionLevel admin ;Require admin rights on NT6+ (When UAC is turned on)

!include LogicLib.nsh
!include EnvVarUpdate.nsh

;--------------------------------
;Interface Settings

  !define MUI_HEADERIMAGE
  !define MUI_HEADERIMAGE_BITMAP "HeaderLucterios.bmp"
  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_LICENSE "License.txt"
  !insertmacro MUI_PAGE_INSTFILES
  !define MUI_FINISHPAGE_TITLE "Install finished"
  !define MUI_FINISHPAGE_RUN "PowerShell.exe -ExecutionPolicy Bypass -File $INSTDIR\launch_lucterios.ps1"
  !define MUI_FINISHPAGE_RUN_TEXT "Launch Lucterios install to configurate your instances"
  !insertmacro MUI_PAGE_FINISH
  
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  
;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "install"
  SectionIn RO
  
  SetOutPath "$INSTDIR"
  File "License.txt"

  SetOutPath "$INSTDIR"
  File "install.ps1"

  ExecWait 'PowerShell.exe -ExecutionPolicy Bypass -File $INSTDIR\install.ps1'

  WriteRegStr HKLM Software\Lucterios2 "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Lucterios2" "DisplayName" "Lucterios"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Lucterios2" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Lucterios2" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Lucterios2" "NoRepair" 1
  WriteUninstaller "uninstall.exe"
 
SectionEnd

Function .onInit
  UserInfo::GetAccountType
  pop $0
  ${If} $0 != "admin" ;Require admin rights on NT4+
      MessageBox mb_iconstop "Administrator permission needed!"
      SetErrorLevel 740 ;ERROR_ELEVATION_REQUIRED
      Quit
  ${EndIf}

FunctionEnd

Function un.onInit
  UserInfo::GetAccountType
  pop $0
  ${If} $0 != "admin" ;Require admin rights on NT4+
      MessageBox mb_iconstop "Administrator permission needed!"
      SetErrorLevel 740 ;ERROR_ELEVATION_REQUIRED
      Quit
  ${EndIf}
FunctionEnd

;--------------------------------

; Uninstaller

Section "Uninstall"
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Lucterios2"
  DeleteRegKey HKLM Software\Lucterios2

  ; Remove shortcuts, if any
  Delete "$DESKTOP\Lucterios.lnk"

  ; Remove directories used
  RMDir /r "$INSTDIR"

SectionEnd