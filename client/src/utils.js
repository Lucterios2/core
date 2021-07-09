'use strict'
const util = require('util')

var __nextobjid = 1
var gServerUrl = null
var gVersionFct = function () {
  return ''
}

export var GWithExtraMenu = true
export var GActiveLog = false
export var GMultiServer = true
export function getServerUrl () {
  if (gServerUrl !== null) {
    return gServerUrl()
  } else {
    return null
  }
}
export function setServerUrl (callBack) {
  gServerUrl = callBack
}
export function setVersionFct (callBack) {
  gVersionFct = callBack
}
export var getVersion = function () {
  return gVersionFct()
}
export function setGlobalParam (aWithExtraMenu, aMultiServer, aActiveLog) {
  GWithExtraMenu = aWithExtraMenu
  GMultiServer = aMultiServer
  GActiveLog = aActiveLog
}

export function createGuid () {
  return __nextobjid++
}

export function unusedVariables () {
  return undefined
}

export var FAILURE = 0
export var CRITIC = 1
export var GRAVE = 2
export var IMPORTANT = 3
export var MINOR = 4

export class LucteriosException {
  constructor (aType, aMessage, aInfo, aExtra) {
    this.type = aType
    this.message = aMessage
    this.info = aInfo
    this.extra = aExtra
  }
  toString () {
    var res = this.type + '~' + this.message
    if (this.info) {
      res += '#' + this.info
      if (this.extra) {
        res += '#' + this.extra
      }
    }
    return res
  }
}

export var FORGOTTEN_CHAR = ':/\\<>| "\''

export class HashMap {
  put (key, value) {
    this[key] = value
  }
  get (key) {
    if (this[key] === undefined) {
      return null
    }
    return this[key]
  }
  val (index) {
    var cursor = 0
    var prop
    for (prop in this) {
      if (this.hasOwnProperty(prop) && (this[prop] !== undefined)) {
        if (cursor === index) {
          return this.get(prop)
        }
        cursor++
      }
    }
    return null
  }
  keys () {
    var result = []
    var prop
    for (prop in this) {
      if (this.hasOwnProperty(prop) && (this[prop] !== undefined)) {
        result.push(prop)
      }
    }
    return result
  }
  size () {
    var count = 0
    var prop
    for (prop in this) {
      if (this.hasOwnProperty(prop)) {
        count++
      }
    }
    return count
  }
  putAll (aOtherMap) {
    var self = this
    aOtherMap.keys().forEach(function (key) {
      self.put(key, aOtherMap[key])
    })
  }

  toString () {
    var result = ''
    var prop
    for (prop in this) {
      if (this.hasOwnProperty(prop) && (this[prop] !== undefined)) {
        result += util.format('%s=\'%s\',', prop, this[prop])
      }
    }
    return result
  }
}

export function convertLuctoriosFormatToHtml (oldText) {
  var newText = oldText.replace('>', '&gt;')
  newText = newText.replace(/</g, '&lt;')
  newText = newText.replace(/\{\[bold\]\}/g, '<b>')
  newText = newText.replace(/\{\[\/bold\]\}/g, '</b>')
  newText = newText.replace(/\{\[italc\]\}/g, '<i>')
  newText = newText.replace(/\{\[\/italc\]\}/g, '</i>')
  newText = newText.replace(/\{\[italic\]\}/g, '<i>')
  newText = newText.replace(/\{\[\/italic\]\}/g, '</i>')
  newText = newText.replace(/\{\[newline\]\}/g, '<br>')
  newText = newText.replace(/\{\[underline\]\}/g, '<u>')
  newText = newText.replace(/\{\[\/underline\]\}/g, '</u>')
  newText = newText.replace(/\{\[center\]\}/g, '<center>')
  newText = newText.replace(/\{\[\/center\]\}/g, '</center>')
  newText = newText.replace(/\{\[hr\/\]\}/g, '<hr/>')
  newText = newText.replace(/<hr>/g, '<hr/>')
  newText = newText.replace(/\{\[br\/\]\}/g, '<br/>')
  newText = newText.replace(/\{\[/g, '<')
  newText = newText.replace(/\]\}/g, '>')
  if ((newText.length > 0) && newText.charAt(0) === '/') {
    newText = '&#47;' + newText.substring(1)
  }
  return newText
}

export function lpad (oldText, padString, length) {
  var str = oldText
  while (str.length < length) {
    str = padString + str
  }
  return str
}

export function getFileNameWithoutForgottenChar (oldText) {
  var newText = oldText
  newText = newText.replace(/:/g, '_')
  newText = newText.replace(/\//g, '_')
  newText = newText.replace(/\\/g, '_')
  newText = newText.replace(/</g, '_')
  newText = newText.replace(/>/g, '_')
  newText = newText.replace(/\|/g, '_')
  newText = newText.replace(/ /g, '_')
  newText = newText.replace(/"/g, '_')
  newText = newText.replace(/'/g, '_')
  return newText.trim()
}

export function postLog (aText) {
  if (GActiveLog) {
    console.log(aText)
  }
}
