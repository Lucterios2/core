'use strict'
/* global jQuery, JsLoadingOverlay */
import { HashMap, getServerUrl, GMultiServer, setVersionFct, setServerUrl, setGlobalParam, convertLuctoriosFormatToHtml, unusedVariables } from './utils.js'
import { HttpTransportImpl } from './transport.js'
import { ActionImpl, FORM_MODAL } from '../src/action.js'
import { SingletonObj, SingletonClose, Singleton, setInitialCallBack, setCleanCallBack, setConfigServers } from './singleton.js'
import { cleanFunction, disconnectFunction, configServers, aboutFunction, helpFunction, insertStyle, refreshFunction } from '../src/tools.js'
import { ObserverFactoryRestImpl } from './observer_factory.js'
import { ObserverAuthentification, WrongObserverAuthentification } from './observer.authentification.js'
import { ObserverAcknowledge } from './observer.acknowledge.js'
import { ObserverException } from './observer.exception.js'
import { ObserverPrint } from './observer.print.js'
import { ObserverDialogBox } from './observer.dialogbox.js'
import { ObserverMenu, infoOpenClose, refreshCurrentAcideMenu, EmptyObserverMenu } from './observer.menu.js'
import { ObserverCustom } from './observer.custom.js'
import 'js-loading-overlay'
import Cookies from 'js-cookie'
const $ = require('jquery')
const util = require('util')
require('jquery-ui-dist/jquery-ui.min.js')
global.jQuery = $

/* ============================ MAIN =========================== */

function standardInitial () {
  cleanFunction()

  if ((SingletonObj !== null) && (Singleton().mDesc !== null)) {
    document.title = Singleton().mDesc.getTitle()
  } else {
    document.title = 'Lucterios'
  }

  SingletonClose()
  Singleton().mWaitingOn = function () {
    JsLoadingOverlay.show({
      'overlayBackgroundColor': '#666666',
      'overlayOpacity': '0.6',
      'spinnerIcon': 'ball-spin',
      'spinnerColor': '#000000',
      'spinnerSize': '3x',
      'overlayIDName': 'overlay',
      'spinnerIDName': 'spinner',
      'offsetX': 0,
      'offsetY': 0,
      'containerID': null,
      'lockScroll': false,
      'overlayZIndex': 9998,
      'spinnerZIndex': 9999
    })
  }
  Singleton().mWaitingOff = function () {
    JsLoadingOverlay.hide()
  }
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

function firstAction () {
  standardInitial()
  var session = Singleton().Transport().getSession()
  if (session === '') {
    Singleton().Factory().setAuthentification('', '')
  } else {
    Singleton().Factory().setAuthentification(null, session)
  }
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
        $('#servers').click(function () { configServers(main) })
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

/* ============================ VIEW =========================== */

var GViewerParams = {}

function viewerReadURL () {
  try {
    window.location.href.replace(location.hash, '').replace(/[?&]+([^=&]+)=?([^&]*)?/gi, function (m, key, value) {
      unusedVariables(m)
      GViewerParams[key] = (value !== undefined) ? value : ''
    })
    GViewerParams = atob(GViewerParams.CODE)
    GViewerParams = jQuery.parseJSON(GViewerParams)
  } catch ($exept) {
    GViewerParams = null
  }
}

function firstViewerAction () {
  var session
  viewerInitial()
  if ((GViewerParams !== null) && (GViewerParams.ses !== undefined)) {
    Singleton().Transport().setSession('')
    Singleton().Transport().setSession(GViewerParams.ses)
    Cookies.set('sessionid', GViewerParams.ses, { path: '/', expires: 0.007 })
  }
  session = Singleton().Transport().getSession()
  if (session === '') {
    Singleton().Factory().setAuthentification('', '')
  } else {
    Singleton().Factory().setAuthentification(null, session)
  }
}

function viewerInitial () {
  cleanFunction()

  if ((SingletonObj !== null) && (Singleton().mDesc !== null)) {
    document.title = Singleton().mDesc.getTitle()
  } else {
    document.title = 'Lucterios'
  }

  SingletonClose()
  Singleton().mWaitingOn = function () {
    JsLoadingOverlay.show({
      'overlayBackgroundColor': '#666666',
      'overlayOpacity': '0.6',
      'spinnerIcon': 'ball-spin',
      'spinnerColor': '#000000',
      'spinnerSize': '3x',
      'overlayIDName': 'overlay',
      'spinnerIDName': 'spinner',
      'offsetX': 0,
      'offsetY': 0,
      'containerID': null,
      'lockScroll': false,
      'overlayZIndex': 9998,
      'spinnerZIndex': 9999
    })
  }
  Singleton().mWaitingOff = function () {
    JsLoadingOverlay.hide()
  }
  Singleton().setHttpTransportClass(HttpTransportImpl)
  Singleton().setFactory(new ObserverFactoryRestImpl())
  Singleton().Factory().setHttpTransport(Singleton().Transport())
  Singleton().setActionClass(ActionImpl)

  Singleton().Factory().clearObserverList()
  Singleton().Factory().AddObserver('core.auth', WrongObserverAuthentification)
  Singleton().Factory().AddObserver('core.menu', EmptyObserverMenu)
  Singleton().Factory().AddObserver('core.dialogbox', ObserverDialogBox)
  Singleton().Factory().AddObserver('core.custom', ObserverCustom)
  Singleton().Factory().AddObserver('core.acknowledge', ObserverAcknowledge)
  Singleton().Factory().AddObserver('core.exception', ObserverException)
  Singleton().Factory().AddObserver('core.print', ObserverPrint)
}

function initialViewerFunction () {
  if (Singleton().mDesc === null) {
    Singleton().close()
    firstViewerAction()
  } else {
    var act
    document.title = util.format('%s - %s', Singleton().mDesc.getTitle(), Singleton().mDesc.getSubTitle())
    if (GViewerParams !== null) {
      if (GViewerParams.bcg === undefined) {
        $('body').css('background', '#EEE url(' + Singleton().mDesc.mBackground + ') repeat')
      } else {
        $('body').css('background', GViewerParams.bcg)
      }
      act = Singleton().CreateAction()
      act.mFormType = FORM_MODAL
      act.initializeEx(null, Singleton().Factory(), '', GViewerParams.ext, GViewerParams.act, GViewerParams.method)
      act.getParameters = function () {
        var param = new HashMap()
        jQuery.each(GViewerParams.params, function (key, data) {
          param.put(key, data)
        })
        return param
      }
      act.actionPerformed()
    }
  }
}

function viewer () {
  viewerReadURL()
  setInitialCallBack(initialViewerFunction)
  setCleanCallBack(cleanFunction)
  firstViewerAction()
}

/* ============================ GLOBAL =========================== */

window.main = function () {
  main()
}

window.viewer = function () {
  viewer()
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
