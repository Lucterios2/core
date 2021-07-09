'use strict'
import { FORM_MODAL, SELECT_NONE } from './action.js'
import { Singleton } from './singleton.js'
import { ObserverCustom } from './observer.custom.js'
const $ = require('jquery')
const util = require('util')

function getServersConf () {
  var serverSize
  var serverIdx
  var serverValue
  var serversConf = {
    current: null,
    list: {}
  }
  serversConf.current = localStorage.getItem('current_server')
  serverSize = localStorage.getItem('current_nb')
  if (serverSize !== null) {
    serverSize = parseInt(serverSize, 10)
    for (serverIdx = 0; serverIdx < serverSize; serverIdx++) {
      serverValue = localStorage.getItem(util.format('server_%s', serverIdx))
      if (serverValue !== null) {
        serverValue = serverValue.split('|')
        serversConf.list[serverValue[0]] = serverValue[1]
        if (serversConf.current === null) {
          serversConf.current = serverValue[1]
        }
      }
    }
  }
  return serversConf
}

function setServersList (serversConf) {
  var serverName
  var serverIdx = 0
  var serverUrlMask = new RegExp('^https?://[a-z0-9/:%_+.,#?!@&=-]+$', 'i')
  var serverNameMask = new RegExp('^[a-z0-9_\\-]+$', 'i')
  localStorage.clear()
  for (serverName in serversConf.list) {
    if (serversConf.list.hasOwnProperty(serverName) && serverNameMask.test(serverName) && serverUrlMask.test(serversConf.list[serverName])) {
      localStorage.setItem(util.format('server_%s', serverIdx), util.format('%s|%s', serverName, serversConf.list[serverName]))
      if (serversConf.current === null) {
        serversConf.current = serversConf.list[serverName]
      }
      serverIdx = serverIdx + 1
    }
  }
  localStorage.setItem('current_nb', util.format('%s', serverIdx))
  localStorage.setItem('current_server', serversConf.current)
}

export class ServerManager {
  constructor () {
    this.mObs = null
  }

  createGui (title, modal, jsonContent) {
    var compIdx
    var actionIdx
    var comp
    this.mObs = new ObserverCustom()
    this.mObs.setSource('', '')
    this.mObs.setContent(jsonContent)
    this.mObs.show(title, modal)
    if (jsonContent.close !== undefined) {
      this.mObs.mCloseAction = { actionPerformed: $.proxy(jsonContent.close.callback, this) }
    }
    for (compIdx = 0; compIdx < jsonContent.comp.length; compIdx++) {
      comp = jsonContent.comp[compIdx]
      if (comp.actions !== undefined) {
        for (actionIdx = 0; actionIdx < comp.actions.length; actionIdx++) {
          this.mObs.mCompList[comp.name].buttons[actionIdx].btnaction.callback = $.proxy(comp.actions[actionIdx].callback, this)
        }
      }
    }
    for (actionIdx = 0; actionIdx < jsonContent.actions.length; actionIdx++) {
      this.mObs.mGUI.mButtons[actionIdx].callback = $.proxy(jsonContent.actions[actionIdx].callback, this)
    }
    this.mObs.mGUI.mButtons[jsonContent.actions.length - 1].mCheckNull = false
    $('#refresh_' + this.mObs.mGUI.mId).parent().find('.ui-dialog-titlebar-close').remove()
    $('#refresh_' + this.mObs.mGUI.mId).remove()
    $('#fullscreen_' + this.mObs.mGUI.mId).remove()
  }

  add () {
    var jsonContent = {}
    jsonContent = {
      comp: [ {
        name: 'image',
        x: 0,
        y: 0,
        rowspan: 4,
        component: 'IMAGE',
        type: ''
      }, {
        name: 'title',
        x: 1,
        y: 1,
        colspan: 3,
        component: 'LABELFORM',
        formatstr: '{[center]}{[b]}{[u]}{0}{[/u]}{[/b]}{[/center]}',
        needed: true
      }, {
        name: 'name',
        x: 1,
        y: 2,
        component: 'EDIT',
        description: Singleton().getTranslate('name'),
        reg_expr: '^[a-z0-9_\\-]+$',
        needed: true
      }, {
        name: 'url',
        x: 1,
        y: 3,
        component: 'EDIT',
        description: Singleton().getTranslate('address'),
        reg_expr: '^https?://[a-z0-9/:%_+.,#?!@&=-]+$',
        needed: true
      } ],
      data: {
        image: 'images/status.png',
        title: Singleton().getTranslate('Add new server address'),
        name: '',
        url: ''
      },
      close: {
        callback: this.show
      },
      actions: [ {
        text: Singleton().getTranslate('Ok'),
        modal: FORM_MODAL,
        close: '1',
        unique: SELECT_NONE,
        extension: 'server',
        action: 'save',
        id: 'server/save',
        params: null,
        callback: this.save,
        icon: 'images/ok.png'

      }, {
        text: Singleton().getTranslate('Close'),
        modal: FORM_MODAL,
        close: '1',
        unique: SELECT_NONE,
        params: null,
        callback: this.show,
        icon: 'images/close.png'
      } ]
    }
    this.createGui(Singleton().getTranslate('Add server'), FORM_MODAL, jsonContent)
  }

  save (aParam) {
    var serversConf = getServersConf()
    serversConf.list[aParam.name] = aParam.url
    setServersList(serversConf)
    this.show()
  }

  deleteItem (aParam) {
    var serversConf = getServersConf()
    if (serversConf.list[aParam.server] !== undefined) {
      delete serversConf.list[aParam.server]
    }
    setServersList(serversConf)
    this.show()
  }

  currentItem (aParam) {
    var serversConf = getServersConf()
    if (serversConf.list[aParam.server] !== undefined) {
      serversConf.current = serversConf.list[aParam.server]
    }
    setServersList(serversConf)
    this.show()
  }

  show () {
    var jsonContent
    var serverName
    var gridContent = {}
    var serversConf = getServersConf()
    gridContent.x = 1
    gridContent.y = 2
    gridContent.name = 'server'
    gridContent.component = 'GRID'
    gridContent.no_pager = true
    gridContent.headers = [
      [ 'name', Singleton().getTranslate('name'), '', 0, '' ],
      [ 'url', Singleton().getTranslate('address'), '', 0, '' ],
      [ 'current', Singleton().getTranslate('current'), 'B', 0, '' ]
    ]
    gridContent.actions = [{
      text: Singleton().getTranslate('current'),
      modal: FORM_MODAL,
      close: '1',
      unique: '0',
      icon: 'images/default.png',
      extension: 'server',
      action: 'current',
      id: 'server/current',
      params: null,
      callback: this.currentItem
    }, {
      text: Singleton().getTranslate('add'),
      modal: FORM_MODAL,
      close: '1',
      unique: '1',
      extension: 'server',
      action: 'add',
      icon: 'images/add.png',
      id: 'server/add',
      params: null,
      callback: this.add
    }, {
      text: Singleton().getTranslate('delete'),
      modal: FORM_MODAL,
      close: '1',
      unique: '0',
      extension: 'server',
      action: 'delete',
      icon: 'images/delete.png',
      id: 'server/delete',
      params: null,
      callback: this.deleteItem
    } ]
    jsonContent = {
      comp: [ {
        name: 'image',
        x: 0,
        y: 0,
        rowspan: 4,
        component: 'IMAGE',
        type: ''
      }, {
        name: 'title',
        x: 1,
        y: 1,
        component: 'LABELFORM',
        formatstr: '{[center]}{[b]}{[u]}{0}{[/u]}{[/b]}{[/center]}'
      }, gridContent ],
      data: {
        image: 'images/status.png',
        title: Singleton().getTranslate('Manage server addresses'),
        server: []
      },
      close: {
        callback: this.reload
      },
      actions: [ {
        text: Singleton().getTranslate('Ok'),
        modal: FORM_MODAL,
        close: 1,
        unique: SELECT_NONE,
        params: null,
        callback: this.reload,
        icon: 'images/ok.png'
      } ]

    }
    for (serverName in serversConf.list) {
      if (serversConf.list.hasOwnProperty(serverName)) {
        jsonContent.data.server.push({
          id: serverName,
          name: serverName,
          url: serversConf.list[serverName],
          current: (serversConf.list[serverName] === serversConf.current)
        })
      }
    }
    this.createGui(Singleton().getTranslate('Servers'), FORM_MODAL, jsonContent)
  }
}

export function getCurrentServerurl () {
  var current = getServersConf().current
  if ((current !== null) && (current.slice(-1) !== '/')) {
    current = current + '/'
  }
  return current
}
