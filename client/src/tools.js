'use strict'
import { HashMap, createGuid, LucteriosException, IMPORTANT, GMultiServer, convertLuctoriosFormatToHtml } from './utils.js'
import { HttpTransportLocal } from './transport.js'
import { ObserverFactoryRestImpl } from './observer_factory.js'
import { Singleton, getDeviceInfo } from './singleton.js'
import { ActionInt } from '../src/action.js'
import { GUIManage, CompBasic, createTable } from './gui.utils.js'
import { ServerManager } from './config_server.js'
const $ = require('jquery')

export function insertStyle (rule) {
  var css = document.createElement('style')
  css.type = 'text/css'
  css.innerHTML = rule
  document.body.appendChild(css)
}

export function cleanFunction () {
  $('body > div').each(function () {
    var id = $(this).attr('id')
    if (id !== 'lucteriosClient') {
      $(this).remove()
    }
  })
}

export function helpFunction () {
  var win = window.open(Singleton().Transport().getIconUrl('Docs'), '_blank')
  win.focus()
}

export function sendSupportFunction () {
  var complement = Singleton().getTranslate('Describ your problem.<br>Thanks<br><br>')
  window.location = Singleton().mDesc.fillEmailSupport(Singleton().getTranslate('Bug report'), complement)
}

export function aboutFunction () {
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

export function configServers (reloadFct) {
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
  serversMng.reload = reloadFct
  serversMng.show()
}

export function aboutMoreFunction () {
  var table = []
  table[0] = []
  table[0][0] = new CompBasic(Singleton().mDesc.getHTML(''))
  this.mGUI = new GUIManage(createGuid(), Singleton().getTranslate('Configuration'), null)
  this.mGUI.addcontent(createTable(table), [])
  this.mGUI.showGUI(true)
}

export function disconnectFunction () {
  var act = Singleton().CreateAction()
  act.initializeEx(null, Singleton().Factory(), '', 'CORE', 'exitConnection')
  act.actionPerformed()
}

export function refreshFunction () {
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
