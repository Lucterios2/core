'use strict'
import { createGuid, HashMap, LucteriosException, IMPORTANT, getServerUrl, GMultiServer, setVersionFct, setServerUrl, setGlobalParam, convertLuctoriosFormatToHtml } from './utils.js'
import { HttpTransportImpl, HttpTransportLocal } from './transport.js'
import { SingletonObj, SingletonClose, Singleton, setInitialCallBack, setCleanCallBack, setConfigServers, getDeviceInfo } from './singleton.js'
import { ActionImpl, ActionInt } from '../src/action.js'
import { GUIManage, CompBasic, createTable } from './gui.utils.js'
import { ObserverFactoryRestImpl } from './observer_factory.js'
import { ObserverAuthentification } from './observer.authentification.js'
import { ObserverAcknowledge } from './observer.acknowledge.js'
import { ObserverException } from './observer.exception.js'
import { ObserverPrint } from './observer.print.js'
import { ObserverDialogBox } from './observer.dialogbox.js'
import { ObserverMenu, infoOpenClose, refreshCurrentAcideMenu } from './observer.menu.js'
import { ObserverCustom } from './observer.custom.js'
import { ServerManager } from './config_server.js'
const $ = require('jquery')
const util = require('util')
require('jquery-ui-dist/jquery-ui.min.js')

function insertStyle (rule) {
  var css = document.createElement('style')
  css.type = 'text/css'
  css.innerHTML = rule
  document.body.appendChild(css)
}

function cleanFunction () {
  $('body > div').each(function () {
    var id = $(this).attr('id')
    if (id !== 'lucteriosClient') {
      $(this).remove()
    }
  })
  $('#lucteriosClient').html('<div class="waiting"/>')
}

function refreshFunction () {
  cleanFunction()
  var act = Singleton().CreateAction()
  act.initializeEx(null, Singleton().Factory(), '', 'CORE', 'authentification', 'POST')
  act.getParameters = function () {
    var param = new HashMap()
    param.put('info', 'true')
    param.put('ses', Singleton().Transport().getSession())
    return param
  }
  act.actionPerformed()
}

function standardInitial () {
  cleanFunction()

  $(document).on({
    ajaxStart: function () {
      $('body').addClass('loading')
    },
    ajaxStop: function () {
      $('body').removeClass('loading')
    }
  })

  if ((SingletonObj !== null) && (Singleton().mDesc !== null)) {
    document.title = Singleton().mDesc.getTitle()
  } else {
    document.title = 'Lucterios'
  }

  SingletonClose()
  Singleton().setHttpTransportClass(HttpTransportImpl)
  Singleton().setFactory(new ObserverFactoryRestImpl())
  Singleton().Factory().setHttpTransport(Singleton().Transport())
  Singleton().setActionClass(ActionImpl)

  Singleton().Factory().clearObserverList()

  Singleton().Factory().AddObserver('core.auth', ObserverAuthentification)
  Singleton().Factory().AddObserver('core.menu', ObserverMenu)
  Singleton().Factory().AddObserver('core.dialogbox', ObserverDialogBox)
  Singleton().Factory().AddObserver('core.custom', ObserverCustom)
  Singleton().Factory().AddObserver('core.acknowledge', ObserverAcknowledge)
  Singleton().Factory().AddObserver('core.exception', ObserverException)
  Singleton().Factory().AddObserver('core.print', ObserverPrint)
}

function disconnectFunction () {
  var act = Singleton().CreateAction()
  act.initializeEx(null, Singleton().Factory(), '', 'CORE', 'exitConnection')
  act.actionPerformed()
}

function firstAction () {
  standardInitial()
  var session = Singleton().Transport().getSession()
  if (session === '') {
    Singleton().Factory().setAuthentification('', '')
  } else {
    Singleton().Factory().setAuthentification(null, session)
  }
}

function configServers () {
  var serversMng
  cleanFunction()
  Singleton().setHttpTransportClass(HttpTransportLocal)
  Singleton().setFactory(new ObserverFactoryRestImpl())
  Singleton().setActionClass(ActionInt)
  Singleton().Factory().clearObserverList()

  document.title = Singleton().getTranslate('Configuration')
  if (GMultiServer === false) {
    throw new LucteriosException(IMPORTANT, 'No configuration !')
  }
  serversMng = new ServerManager()
  serversMng.reload = main
  serversMng.show()
}

function aboutMoreFunction () {
  var table = []
  table[0] = []
  table[0][0] = new CompBasic(Singleton().mDesc.getHTML(''))
  this.mGUI = new GUIManage(createGuid(), Singleton().getTranslate('Configuration'), null)
  this.mGUI.addcontent(createTable(table), [])
  this.mGUI.showGUI(true)
}

function helpFunction () {
  var win = window.open(Singleton().Transport().getIconUrl('Docs'), '_blank')
  win.focus()
}

function sendSupportFunction () {
  var complement = Singleton().getTranslate('Describ your problem.<br>Thanks<br><br>')
  window.location = Singleton().mDesc.fillEmailSupport(Singleton().getTranslate('Bug report'), complement)
}

function aboutFunction () {
  var mDescription = Singleton().mDesc
  var table = []
  var html
  var acts = []
  table[0] = []
  table[0][0] = new CompBasic('<img src="' + mDescription.getLogoIconName() + '">', 1, 2)
  table[0][1] = new CompBasic('<center><h1>' + mDescription.getTitle() + '</h1></center>', 2, 1)
  table[1] = []
  table[1][1] = new CompBasic('<table width="100%">' +
      '<tr><td><center>' +
      Singleton().getTranslate('Version') +
      '</center></td><td><center>' +
      mDescription.getApplisVersion() +
      '</center></td></tr>' +
      '<tr><td colspan="2"><font size="-1"><center><i>' +
      mDescription.getCopyRigth() +
      '</i></center></font></td><td>' +
      '</table>', 2, 1)

  table[2] = []
  table[2][0] = new CompBasic('<HR SIZE="2" WIDTH="100%" ALIGN=center>' +
      '<table width="100%">' +
      '<tr><td colspan="2"><font size="+1"><center>' +
      Singleton().getTranslate('Use the <i>Lucterios</i> framework') +
      '</center></font></td><td>' +
      '<tr><td><center>' +
      Singleton().getTranslate('Server') +
      '</center></td><td><center>' +
      mDescription.getServerVersion() +
      '</center></td></tr>' +
      '<tr><td><center>' +
      Singleton().getTranslate('Cordova client') +
      '</center></td><td><center>' +
      mDescription.getCordovaVersionCurrent() +
      '</center></td></tr>' +
      '<tr><td><center>' +
      Singleton().getTranslate('Device client') +
      '</center></td><td><center>' +
      getDeviceInfo() +
      '</center></td></tr>' +
      '</table>', 3)
  table[3] = []
  table[3][0] = new CompBasic('<center><img src="images/LucteriosImage.png"></center>', 3)
  table[4] = []
  table[4][0] = new CompBasic('<center><font size="-1"><center><i>' +
      Singleton().getTranslate('Tool of customize management on GPL license') +
      '</i></center></font></center>', 3)
  table[5] = []
  html = '<center>'
  html += '<a target="_blank" href="http://www.lucterios.org" style="margin-right:5px;">http://www.lucterios.org</a> '
  html += '<a target="_blank" href="http://www.sd-libre.fr" style="margin-left:5px;">http://www.sd-libre.fr</a><br/>'
  html += Singleton().getTranslate('Thank you for supporting our work.')
  html += '<form id="formDon" target="_blank" action="https://www.paypal.com/cgi-bin/webscr" method="post">'
  html += '<input name="cmd" value="_s-xclick" type="hidden">'
  html += '<input name="hosted_button_id" value="BDGPMSZGYLWT6" type="hidden">'
  html += '<input style="border: 0;" alt="PayPal" name="submit" src="images/bouton-don-v.png" type="image"></form>'
  html += '</center><hr/>'
  table[5][0] = new CompBasic(html, 3)

  table[6] = []
  table[6][0] = new CompBasic(convertLuctoriosFormatToHtml(mDescription.mSupportHTML), 3)

  this.mGUI = new GUIManage(createGuid(), Singleton().getTranslate('About...'), null)

  acts[0] = new ActionInt()
  acts[0].initializeEx(null, null, Singleton().getTranslate('ask support'))
  acts[0].mIcon = 'images/right.png'
  acts[0].callback = sendSupportFunction
  acts[1] = new ActionInt()
  acts[1].initializeEx(null, null, Singleton().getTranslate('More...'))
  acts[1].mIcon = 'images/info.png'
  acts[1].callback = aboutMoreFunction
  acts[2] = new ActionInt()
  acts[2].initializeEx(null, null, Singleton().getTranslate('Close'))
  acts[2].mIcon = 'images/close.png'
  acts[2].callback = $.proxy(this.mGUI.close, this.mGUI)

  this.mGUI.addcontent(createTable(table), acts)
  this.mGUI.showGUI(true)
}

function initialFunction (aInitialHeader) {
  if (Singleton().mDesc === null) {
    Singleton().close()
    firstAction()
  } else {
    var disconnectTitle, html, act
    if (aInitialHeader) {
      $('div#message_before').remove()
      disconnectTitle = Singleton().getTranslate('Logoff')
      if (Singleton().mDesc.getLogin() === '') {
        disconnectTitle = Singleton().getTranslate('Logon')
      }
      html = '<div id="status">'
      html += '<div class="header-left">'
      html += '<label id="showmenu" class="ui-widget-header ui-corner-all">'
      html += '<span class="fa fa-list-alt"/>' + '<span name="headertle">'
      html += Singleton().getTranslate('Info')
      html += '</span>'
      html += '</label>'
      html += util.format('<img src="%s" style="height:48px">', Singleton().mDesc.getLogoIconName())
      html += '<label id="statususer">'
      html += Singleton().mDesc.getConnectUser()
      html += '</label>'
      html += '</div>'
      html += '<div class="header-right">'
      html += '<label id="disconnect" class="ui-widget-header ui-corner-all" >'
      html += '<span class="fa fa-power-off"/>' + '<span name="headertle">'
      html += disconnectTitle
      html += '</span>'
      html += '</label>'
      html += '<label id="refresh" class="ui-widget-header ui-corner-all" >'
      html += '<span class="fa fa-refresh"/>'
      html += '<span name="headertle">'
      html += Singleton().getTranslate('Refresh')
      html += '</span>'
      html += '</label>'
      if (GMultiServer === true) {
        html += '<label id="servers" class="ui-widget-header ui-corner-all" >'
        html += '<span class="fa fa-database"/>'
        html += '<span name="headertle">'
        html += Singleton().getTranslate('Servers')
        html += '</span>'
        html += '</label>'
      }
      html += '<label id="about" class="ui-widget-header ui-corner-all" >'
      html += '<span class="fa fa-info-circle"/>'
      html += '<span name="headertle">'
      html += Singleton().getTranslate('About...')
      html += '</span>'
      html += '</label>'
      html += '<label id="help" class="ui-widget-header ui-corner-all" >'
      html += '<span class="fa fa-question-circle"/>'
      html += '<span name="headertle">'
      html += Singleton().getTranslate('Help')
      html += '</span>'
      html += '</label>'
      html += '</div>'
      html += '</div>'
      $('#lucteriosClient').append(html)
      $('#refresh').click(refreshFunction)
      if (Singleton().mDesc.getMode() === '2') {
        $('#disconnect').css('visibility', 'hidden')
      } else {
        $('#disconnect').click(disconnectFunction)
      }
      if (GMultiServer === true) {
        $('#servers').click(configServers)
      }
      $('#about').click(aboutFunction)
      $('#help').click(helpFunction)
      $('#showmenu').click(infoOpenClose)
      if (Singleton().mRefreshMenu) {
        act = Singleton().CreateAction()
        act.initializeEx(null, Singleton().Factory(), '', 'CORE', 'menu')
        act.actionPerformed()
      }
    } else {
      if (Singleton().mDesc.mMessageBefore !== '') {
        html = '<div id="message_before">'
        html += convertLuctoriosFormatToHtml(Singleton().mDesc.mMessageBefore)
        html += '</div>'
        $('#lucteriosClient').append(html)
      }
    }
    document.title = util.format('%s - %s', Singleton().mDesc.getTitle(), Singleton().mDesc.getSubTitle())
    if (Singleton().mDesc.mBackground !== '') {
      $('body').css('background', '#EEE url(' + Singleton().mDesc.mBackground + ') repeat')
    } else {
      $('body').css('background', '')
    }
    $('style[type="text/css"]').remove()
    if (Singleton().mDesc.mStyle !== '') {
      insertStyle(Singleton().mDesc.mStyle)
    }
  }
}

function main () {
  setInitialCallBack(initialFunction)
  setCleanCallBack(cleanFunction)
  setConfigServers(configServers)
  setInterval(refreshCurrentAcideMenu, 5 * 60 * 1000) // Watchdog 5 min
  if (getServerUrl() !== null) {
    firstAction()
  } else {
    configServers()
  }
}

window.main = function () {
  main()
}

window.setVersionFct = function (callBack) {
  setVersionFct(callBack)
}

window.setServerUrl = function (callBack) {
  setServerUrl(callBack)
}

window.setGlobalParam = function (aWithExtraMenu, aMultiServer, aActiveLog) {
  setGlobalParam(aWithExtraMenu, aMultiServer, aActiveLog)
}
