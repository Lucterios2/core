'use strict'
/* global Uint8Array, URL, device */

import { HashMap } from './utils.js'
import { gTranslation } from './language.js'
const $ = require('jquery')
const util = require('util')
const FileReader = require('filereader')
const atob = require('atob')

export var SingletonObj = null
export var gInitialCallBack = null
export var gCleanCallBack = null
export var gConfigServers = null

export function setInitialCallBack (callBack) {
  gInitialCallBack = callBack
}
export function setCleanCallBack (callBack) {
  gCleanCallBack = callBack
}
export function runCleanCallBack () {
  if (gCleanCallBack !== null) {
    gCleanCallBack()
  }
}
export function setConfigServers (callBack) {
  gConfigServers = callBack
}

export class FileManager {
  saveBlob (aBlob, aFileName) {
    var self = this
    var reader = new FileReader()
    reader.onload = function (event) {
      var content = event.target.result
      var pos
      if (content.substr(0, 5) === 'data:') {
        pos = content.indexOf(';base64,')
        content = content.substr(pos + 8)
      }
      self.saveFile(content, aFileName)
    }
    reader.readAsDataURL(aBlob)
  }

  saveFile (aContent, aFileName) {
    var offset
    var blob
    var sliceSize = 512
    var byteCharacters = atob(aContent)
    var byteArrays
    var idx
    var byteArray
    var byteNumbers
    var slice
    var mouseEvent
    var hyperlink
    byteArrays = new [].constructor()
    for (offset = 0; offset < byteCharacters.length; offset += sliceSize) {
      slice = byteCharacters.slice(offset, offset + sliceSize)
      byteNumbers = new [].constructor(slice.length)
      for (idx = 0; idx < slice.length; idx++) {
        byteNumbers[idx] = slice.charCodeAt(idx)
      }
      byteArray = new Uint8Array(byteNumbers)
      byteArrays.push(byteArray)
    }
    blob = new Blob(byteArrays, {
      type: 'application/x-json'
    })
    if (window.navigator.msSaveOrOpenBlob) {
      window.navigator.msSaveOrOpenBlob(blob, aFileName)
    } else {
      hyperlink = document.createElement('a')
      hyperlink.href = URL.createObjectURL(blob)
      hyperlink.target = '_blank'
      hyperlink.download = aFileName
      mouseEvent = document.createEvent('MouseEvent')
      mouseEvent.initMouseEvent('click', true, true, window, 0, 0, 0, 80, 20, false, false, false, false, 0, null)
      hyperlink.dispatchEvent(mouseEvent)
      if (window.URL) {
        window.URL.revokeObjectURL(hyperlink.href)
      } else if (window.webkitURL) {
        window.webkitURL.revokeObjectURL(hyperlink.href)
      }
    }
  }

  oldSaveFile (aContent, aFileName) {
    var hyperlink = document.createElement('a')
    var mouseEvent
    hyperlink.href = 'data:application/x-json;base64,' + aContent
    hyperlink.target = '_blank'
    hyperlink.download = aFileName

    mouseEvent = document.createEvent('MouseEvent')
    mouseEvent.initMouseEvent('click', true, true, window, 0, 0, 0, 80, 20, false, false, false, false, 0, null)
    hyperlink.dispatchEvent(mouseEvent)
    if (window.URL) {
      window.URL.revokeObjectURL(hyperlink.href)
    } else if (window.webkitURL) {
      window.webkitURL.revokeObjectURL(hyperlink.href)
    }
  }
}

export class SingletonClass {
  constructor () {
    this.mTransportClass = null
    this.mActionClass = null
    this.mTransportObj = null
    this.mFactory = null
    this.mDesc = null
    this.mRefreshMenu = true
    this.mFileManager = new FileManager()
    this.mActionList = new HashMap()
    this.mSelectLang = null
  }

  getSelectLang () {
    if ((this.mSelectLang === null) && (this.mDesc !== null) && (this.mDesc.getLanguage() !== '')) {
      this.mSelectLang = this.mDesc.getLanguage()
      if ($.datepicker.regional.hasOwnProperty(this.mSelectLang)) {
        $.datepicker.setDefaults($.datepicker.regional[this.mSelectLang])
      }
    }
    if (this.mSelectLang === null) {
      return 'fr'
    }
    return this.mSelectLang
  }

  getTranslate (name) {
    var res = null
    var selectlang = this.getSelectLang()
    if (gTranslation.get(selectlang) !== null) {
      res = gTranslation.get(selectlang).get(name)
    }
    if (res === null) {
      res = name
    }
    return res
  }

  setHttpTransportClass (aTransportClass) {
    this.mTransportObj = null
    this.mTransportClass = aTransportClass
  }

  setActionClass (aActionClass) {
    this.mActionObj = null
    this.mActionClass = aActionClass
  }

  setFactory (aFactory) {
    this.mFactory = aFactory
  }

  Factory () {
    return this.mFactory
  }

  Transport () {
    if (this.mTransportObj === null) {
      var NewTransportClass = this.mTransportClass
      this.mTransportObj = new NewTransportClass()
    }
    return this.mTransportObj
  }

  CreateAction () {
    if (this.mActionClass !== null) {
      var NewActionClass = this.mActionClass
      return new NewActionClass()
    }
    return null
  }

  setInfoDescription (aDesc, aRefreshMenu, aInitialHeader) {
    this.mDesc = aDesc
    this.mSelectLang = null
    this.mRefreshMenu = aRefreshMenu
    if (gInitialCallBack !== null) {
      gInitialCallBack(aInitialHeader)
    }
  }

  close () {
    if (this.mTransportObj !== null) {
      this.mTransportObj.close()
      this.mTransportObj = null
    }
    this.mDesc = null
    this.mRefreshMenu = ''
    this.mFactory = null
  }
}

export var Singleton = function () {
  if (SingletonObj === null) {
    SingletonObj = new SingletonClass()
  }
  return SingletonObj
}

export var SingletonClose = function () {
  if (SingletonObj !== null) {
    SingletonObj.close()
  }
  SingletonObj = null
}

export var getDeviceInfo = function () {
  return Singleton().getTranslate(util.format('%s on %s', device.platform, device.model))
}
