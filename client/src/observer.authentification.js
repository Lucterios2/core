'use strict'
import { HashMap, getVersion, unusedVariables, getServerUrl, LucteriosException, IMPORTANT, GMultiServer, convertLuctoriosFormatToHtml } from './utils.js'
import { CompBasic, GUIManage, createTable } from './gui.utils.js'
import { Singleton, gConfigServers, runCleanCallBack, getDeviceInfo } from './singleton.js'
import { ActionInt } from './action.js'
import { ObserverAbstract } from './observer.js'
const $ = require('jquery')
const util = require('util')

export class ApplicationDescription {
  constructor (aTitle, aCopyRigth, aAppliVersion, aServerVersion) {
    this.mTitle = aTitle
    this.mApplisVersion = aAppliVersion
    this.mServerVersion = aServerVersion
    this.mCopyRigth = aCopyRigth
    this.mCordovaVersionCurrent = getVersion()
    this.mCordovaVersionExpected = ''
    this.mLogoIconName = ''
    this.mBackground = ''
    this.mStyle = ''
    this.mLogin = ''
    this.mInfoServer = ''
    this.mSupportEmail = ''
    this.mSupportHTML = ''
    this.mSubTitle = ''
    this.mRealName = ''
    this.mInstanceName = ''
    this.mMessageBefore = ''
    this.mMode = 0
    this.mLoginField = 'username'
    this.mLanguage = ''
  }

  setLogoIconName (aLogoIconName) {
    this.mLogoIconName = aLogoIconName
  }

  setBackground (aBackground) {
    this.mBackground = aBackground
  }

  setStyle (aStyle) {
    this.mStyle = aStyle
  }

  getTitle () {
    return this.mTitle
  }

  getConnectUser () {
    var res = this.mRealName
    if (this.mLogin !== '') {
      res += util.format(' (%s@%s)', this.mLogin, this.mInstanceName)
    } else {
      res += util.format(' @%s', this.mInstanceName)
    }
    return res
  }

  getLogoIconName () {
    return this.mLogoIconName
  }

  getApplisVersion () {
    return this.mApplisVersion
  }

  getServerVersion () {
    return this.mServerVersion
  }

  getCopyRigth () {
    return this.mCopyRigth
  }

  getInfoServer () {
    return this.mInfoServer
  }

  getSupportEmail () {
    return this.mSupportEmail
  }

  getSupportHTML () {
    return this.mSupportHTML
  }

  getLogin () {
    return this.mLogin
  }

  getSubTitle () {
    return this.mSubTitle
  }

  getRealName () {
    return this.mRealName
  }

  getMode () {
    return this.mMode
  }

  getLoginField () {
    return this.mLoginField
  }

  setLogin (aLogin) {
    this.mLogin = aLogin
  }

  setInfoServer (aInfoServer) {
    this.mInfoServer = aInfoServer
    if (Array.isArray(this.mInfoServer)) {
      this.mInfoServer = this.mInfoServer.join('{[br/]}')
    }
  }

  setSupportEmail (aSupportEmail) {
    this.mSupportEmail = aSupportEmail
  }

  setSupportHTML (aSupportHTML) {
    this.mSupportHTML = aSupportHTML
  }

  setSubTitle (aSubTitle) {
    this.mSubTitle = aSubTitle
  }

  setRealName (aRealName) {
    this.mRealName = aRealName
  }

  setMode (aMode) {
    this.mMode = aMode
  }

  setLoginField (aLoginField) {
    this.mLoginField = aLoginField || 'username'
  }

  setInstanceName (aInstanceName) {
    this.mInstanceName = aInstanceName
  }

  setMessageBefore (aMessageBefore) {
    this.mMessageBefore = aMessageBefore
  }

  getLanguage () {
    return this.mLanguage
  }

  setLanguage (language) {
    this.mLanguage = language
  }

  getCordovaVersionExpected () {
    return this.mCordovaVersionExpected
  }

  setCordovaVersionExpected (cordovaVersionExpected) {
    this.mCordovaVersionExpected = cordovaVersionExpected
  }

  isCordovaVersionOk () {
    var versionExpected
    var versionCurrent
    var result = true
    if (this.mCordovaVersionExpected !== undefined) {
      versionExpected = this.mCordovaVersionExpected.split('.')
      versionCurrent = this.mCordovaVersionCurrent.split('.')
      result = (parseInt(versionExpected[0], 10) === parseInt(versionCurrent[0], 10)) &&
        (parseInt(versionExpected[1], 10) === parseInt(versionCurrent[1], 10)) &&
        (parseInt(versionExpected[2], 10) <= parseInt(versionCurrent[2], 10))
    }
    return result
  }

  getCordovaVersionCurrent () {
    var result = this.mCordovaVersionCurrent
    if (!this.isCordovaVersionOk()) {
      result = util.format('<u>%s (%s)</u>', result, Singleton().getTranslate('Client obselete').replace('<br/>', ':'))
    }
    return result
  }

  fillEmailSupport (aTitle, aComplement) {
    var email = this.mSupportEmail
    var url = 'mailto:' + email
    url += '?subject=' + aTitle
    url += '&body=' + this.getText(aComplement).replace('+', ' ')
    return url
  }

  getHTML (aComplement) {
    var resValue = ''
    if ((aComplement !== null) && (aComplement.length > 0)) {
      resValue += aComplement + '<br>'
    }
    resValue += '<hr><center><h1>' +
      this.mTitle +
      '</h1></center>' +
      '<table width=\'100%\'>' +
      '<tr><td><center>' + Singleton().getTranslate('Version') +
      '</center></td><td><center>' + this.mApplisVersion + '</center></td></tr>' +
      '<tr><td><center>' + Singleton().getTranslate('Server') +
      '</center></td><td><center>' + this.mServerVersion + '</center></td></tr>' +
      '<tr><td><center>' + Singleton().getTranslate('Cordova client') + '</center></td>' +
      '<td><center>' + this.getCordovaVersionCurrent() + '</center></td></tr>' +
      '<tr><td><center>' + Singleton().getTranslate('Device client') + '</center></td>' +
      '<td><center>' + getDeviceInfo() + '</center></td></tr>' +
      '<tr><td><center>' + Singleton().getTranslate('Connection') + '</center></td>' +
      '<td><center><font size=\'-1\'>' + this.getConnectUser() + '<br>' + getServerUrl() + '</font></center></td></tr>' +
      '<tr><td colspan=\'2\'><center><font size=\'-1\'><i>' + this.mCopyRigth + '</i></font></center></td></tr>' +
      '</table><hr>'
    if ((this.mInfoServer !== null) && (this.mInfoServer.length > 0)) {
      resValue += convertLuctoriosFormatToHtml(this.mInfoServer) + '<br>'
    }
    return resValue
  }

  getText (aComplement) {
    var textHtml = this.getHTML(aComplement)
    var pos1 = 1
    var pos2 = 1
    while ((pos1 > 0) && (pos2 > 0)) {
      pos1 = textHtml.indexOf('<style type=\'text/css\'>')
      pos2 = textHtml.indexOf('</style>')
      if ((pos1 > 0) && (pos2 > 0)) {
        textHtml = textHtml.substring(0, pos1) + textHtml.substring(pos2 + 10)
      }
    }
    textHtml = textHtml.replace(
      /(<center>|<\/center>|<table width='100%'>|<\/table>|<tr><td>|<tr><td colspan='2'>|<font size='-1'>|<\/font>|<i>|<\/i>)/g, '')
    textHtml = textHtml.replace(/<h1>\s*/g, '#### ')
    textHtml = textHtml.replace(/[<br>|\\s|\n]*<\/h1>/g, ' ####\n')
    textHtml = textHtml.replace('<b>', '[')
    textHtml = textHtml.replace('</b>', ']')
    textHtml = textHtml.replace('&#60;', '<')
    textHtml = textHtml.replace('&#61;', '=')
    textHtml = textHtml.replace('&#62;', '>')
    textHtml = textHtml.replace('&#95;', '_')
    textHtml = textHtml.replace('&#39;', '\'')
    textHtml = textHtml.replace('&#32;', ' ')
    textHtml = textHtml.replace('&#33;', '!')
    textHtml = textHtml.replace('&#91;', '[')
    textHtml = textHtml.replace('&#93;', ']')
    textHtml = textHtml.replace('&#47;', '/')
    textHtml = textHtml.replace(/(<\/td><\/tr>|<br>|<br\/>)/g, '\n')
    textHtml = textHtml.replace(/<\/td><td>/g, ' : ')
    textHtml = textHtml.replace(/(<hr>|<hr\/>)/g, '__________________________________________\n')
    return encodeURIComponent(textHtml)
  }
}

export class ObserverAuthentification extends ObserverAbstract {
  constructor () {
    super()
    this.refreshMenu = true
    this.acts = null
    this.mActions = null
  }

  getObserverName () {
    return 'core.auth'
  }

  setContent (aJSON) {
    var extraId
    super.setContent(aJSON)
    this.acts = []
    this.acts[0] = new ActionInt()
    this.acts[0].initializeEx(this, null, 'Ok')
    this.acts[0].mIcon = 'images/ok.png'
    this.acts[0].callback = $.proxy(function (aParams) {
      if (this.mGUI !== null) {
        var login = aParams.get('login')
        var pass = aParams.get('password')
        Singleton().Factory().setAuthentification(login, pass)
      }
    }, this)
    if (GMultiServer === true) {
      this.acts[1] = new ActionInt()
      this.acts[1].initializeEx(null, null, Singleton().getTranslate('Servers'))
      this.acts[1].mIcon = 'images/status.png'
      this.acts[1].callback = gConfigServers
      extraId = 2
    } else {
      extraId = 1
    }
    this.acts[extraId] = new ActionInt()
    this.acts[extraId].initializeEx(this, Singleton().Factory(), Singleton().getTranslate('Cancel'))
    this.acts[extraId].mIcon = 'images/cancel.png'
    this.acts[extraId].callback = function () {
      Singleton().setInfoDescription(null, false)
    }
    this.mActions = this.mJSON.actions
  }

  getDesc () {
    var jsonConnection
    var desc = null
    if (this.mJSON.connexion !== undefined) {
      jsonConnection = this.mJSON.connexion
      desc = new ApplicationDescription(jsonConnection.TITLE, jsonConnection.COPYRIGHT, jsonConnection.VERSION,
        jsonConnection.SERVERVERSION)
      desc.setCordovaVersionExpected(jsonConnection.CORDOVAVERSION)
      desc.setLogoIconName(jsonConnection.LOGONAME)
      desc.setBackground(jsonConnection.BACKGROUND)
      desc.setStyle(jsonConnection.STYLE)
      desc.setSupportEmail(jsonConnection.EMAIL)
      desc.setSupportHTML(jsonConnection.SUPPORT_HTML)
      desc.setInfoServer(jsonConnection.INFO_SERVER)
      desc.setSubTitle(jsonConnection.SUBTITLE)
      desc.setLogin(jsonConnection.LOGIN)
      desc.setRealName(jsonConnection.REALNAME.trim())
      desc.setMode(jsonConnection.MODE)
      desc.setLoginField(jsonConnection.LOGIN_FIELD)
      desc.setInstanceName(jsonConnection.INSTANCE)
      desc.setMessageBefore(jsonConnection.MESSAGE_BEFORE)
      desc.setLanguage(jsonConnection.LANGUAGE)
    }
    return desc
  }

  show (aTitle, aGUIType) {
    super.show(aTitle, aGUIType)
    var cdate = this.mJSON.data
    var desc = this.getDesc()
    if (cdate !== 'OK') {
      Singleton().Transport().setSession('')
      runCleanCallBack()
      Singleton().mDesc = desc
      this.showLogon(cdate)
      Singleton().setInfoDescription(desc, false, false)
      this.refreshMenu = true
    } else {
      if ((this.mJSON.context !== undefined) && (this.mJSON.context.ses !== undefined)) {
        Singleton().Transport().setSession(this.mJSON.context.ses)
      }
      Singleton().setInfoDescription(desc, this.refreshMenu, true)
      this.refreshMenu = false
    }
  }

  getParameters (aCheckNull) {
    unusedVariables(aCheckNull)
    var requete = new HashMap()
    var jcnt
    var login
    var pass
    if (this.mGUI !== null) {
      jcnt = this.mGUI.getHtmlDom()
      login = jcnt.find('table:eq(0) > tbody > tr:eq(1) > td:eq(1) > input')
      requete.put('login', login.val())
      pass = jcnt.find('table:eq(0) > tbody > tr:eq(2) > td:eq(1) > input')
      requete.put('password', pass.val())
      $('#frm_' + this.mGUI.mId).submit()
    }
    return requete
  }

  closeEx () {
    if (this.mGUI !== null) {
      this.mGUI.dispose()
    }
  }

  getRefreshMenu () {
    return this.refreshMenu
  }

  showLogon (cdate) {
    var text = ''
    var table = []
    var index
    var logboxId
    var extraActs = []
    var extraTable = []
    var loginTxt = Singleton().getTranslate('Username')
    if (Singleton().mDesc.getLoginField() === 'email') {
      loginTxt = Singleton().getTranslate('Email')
    }
    if (Singleton().Transport().getLastLogin() !== '') {
      if (cdate === 'BADAUTH') {
        if (Singleton().mDesc.getLoginField() === 'email') {
          text = Singleton().getTranslate('Email or password wrong!')
        } else {
          text = Singleton().getTranslate('Username or password wrong!')
        }
      } else if (cdate === 'NEEDAUTH') {
        text = Singleton().getTranslate('Please, identify you')
      } else if (cdate === 'ONLYADMIN') {
        text = Singleton().getTranslate('Only administrators can access!')
      } else if (cdate !== '') {
        text = '\'' + cdate + '\''
      }
    }

    table[0] = []
    table[0][0] = new CompBasic('<label style=\'width:100%;text-align:center;color:red;\'>' + text + '</label>', 2)

    table[1] = []
    table[1][0] = new CompBasic('<span style=\'width:95%;margin:5px;\'><b>' + loginTxt + '</b></span>')
    table[1][1] = new CompBasic('<input name=\'login\' type=\'text\' style=\'width:95%;\'/>')

    table[2] = []
    table[2][0] = new CompBasic('<span style=\'width:95%;margin:5px;\'><b>' + Singleton().getTranslate('Password') + '</b></span>')
    table[2][1] = new CompBasic('<input name=\'password\' type=\'password\' style=\'width:95%;\'/>')
    if (this.mActions) {
      extraTable[0] = []
      for (index = 0; index < this.mActions.length; index++) {
        extraActs[index] = Singleton().CreateAction()
        extraActs[index].initialize(this, Singleton().Factory(), this.mActions[index])
        extraTable[0][index] = new CompBasic(util.format('<center><button id=\'btn_%s_%s\'><span style=\'font-size:10px;\'>%s</span></button></center>', this.getId(), index, extraActs[index].getTitle()))
      }
      table[3] = []
      table[3][0] = new CompBasic(createTable(extraTable), 2)
    }
    this.mGUI = new GUIManage(this.getId(), Singleton().getTranslate('Logon'), this)
    this.mGUI.withForm = true
    this.mGUI.addcontent(createTable(table), this.acts)
    this.mGUI.showGUI(true)
    $('#' + this.getId()).dialog('option', 'height', 'auto')
    $('#' + this.getId()).dialog('option', 'width', 'auto')
    for (index = 0; index < extraActs.length; index++) {
      $(util.format('#btn_%s_%s', this.getId(), index)).click($.proxy(extraActs[index].actionPerformed, extraActs[index]))
    }
    logboxId = this.mGUI.mId
    $('#frm_' + logboxId).submit(function (event) {
      event.preventDefault()
    })

    $('#frm_' + logboxId).find('[name=\'password\'],[name=\'login\']').bind('keydown', function (event) {
      var result
      var btns
      var keycode = (event.keyCode || event.which || event.charCode)
      if (keycode === 13) {
        btns = $('div.ui-dialog-buttonset > button.ui-button')
        btns[0].click()
        result = false
      } else {
        result = true
      }
      return result
    })
  }
}

export class WrongObserverAuthentification extends ObserverAuthentification {
  getObserverName () {
    return 'core.auth'
  }

  showLogon (cdate) {
    var text = ''
    if (cdate === 'BADAUTH') {
      text = Singleton().getTranslate('Login or password wrong!', 'Alias ou Mot de passe incorrect!')
    } else if (cdate === 'NEEDAUTH') {
      text = Singleton().getTranslate('Please, identify you')
    } else if (cdate === 'ONLYADMIN') {
      text = Singleton().getTranslate('Only administrators can access!')
    } else if (cdate !== '') {
      text = '\'' + cdate + '\''
    }
    throw new LucteriosException(IMPORTANT, text)
  }
}
