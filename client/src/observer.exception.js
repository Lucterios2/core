'use strict'
import { GMultiServer, FAILURE, CRITIC, GRAVE, IMPORTANT, MINOR, convertLuctoriosFormatToHtml } from './utils.js'
import { CompBasic, GUIManage, createTable, createTab } from './gui.utils.js'
import { ObserverAbstract } from './observer.js'
import { Singleton, gConfigServers } from './singleton.js'
import { ActionInt } from './action.js'
const $ = require('jquery')

export class ObserverException extends ObserverAbstract {
  constructor () {
    super()
    this.message = ''
    this.code = 0
    this.mode = 0
    this.debugInfo = ''
    this.type = ''
    this.userInfo = ''
    this.stackText = ''
    this.requette = ''
  }

  getObserverName () {
    return 'core.exception'
  }

  setContent (aJSON) {
    super.setContent(aJSON)
    var jsonError = this.mJSON.exception
    this.message = jsonError.message
    this.code = parseInt('0' + jsonError.code, 10)
    this.debugInfo = jsonError.debug
    this.type = jsonError.type

    this.requette = jsonError.requette || ''
    if (this.requette === '') {
      this.requette = Singleton().Factory().mParameters
    }
    if (this.requette === '*') {
      this.requette = ''
    }
    this.reponse = jsonError.response || ''
    this.stackText = this.getStackText()
  }

  getInfo (aInfo) {
    var res = aInfo.replace(/\n/g, '***')
    res = $('<div />').text(res).html()
    return res.replace(/\*\*\*/g, '\n').replace(/></g, '>\n<')
  }

  getStackText () {
    var stackText = ''
    var stackTexts = this.debugInfo.split('{[br/]}')
    var sIdx
    var stackLines
    for (sIdx = 0; sIdx < stackTexts.length; sIdx++) {
      stackLines = stackTexts[sIdx].split('|')
      if (stackLines.length === 1) {
        stackText += stackLines
      } else {
        if (stackLines.length > 1) {
          stackText += stackLines[1].rpad(' ', 50)
        }
        if (stackLines.length > 2) {
          stackText += stackLines[2].rpad(' ', 5)
        }
        if (stackLines.length > 3) {
          stackText += stackLines[3]
        }
      }
      stackText += '\n'
    }
    return stackText.trim()
  }

  show (aTitle, aGUIType) {
    super.show(aTitle, aGUIType)
    this.setActive(true)
    this.exceptShow()
    this.close()
  }

  exceptShow () {
    var jcnt
    var errTitle = ''
    var imageName = ''
    var imageUrl = ''
    var table = []
    var acts = []
    var titles = []
    var contents = []
    var extraId
    var rep
    var pos
    var comp
    var currentGui
    var self
    switch (this.code) {
      case FAILURE:
      case CRITIC:
        imageName = 'error'
        errTitle = Singleton().getTranslate('Error')
        break
      case GRAVE:
      case IMPORTANT:
        imageName = 'warning'
        errTitle = Singleton().getTranslate('Warning')
        break
      case MINOR:
        imageName = 'info'
        errTitle = Singleton().getTranslate('Information')
        break
      default:
        imageName = 'error'
        errTitle = Singleton().getTranslate('Error')
        break
    }
    imageUrl = 'images/' + imageName + '.png'
    table[0] = []
    table[0][0] = new CompBasic('<img src=\'' + imageUrl + '\' alt=\'' + imageName + '\'></img>')
    table[0][1] = new CompBasic('<label style=\'max-width:800px;overflow:auto;\'><b>' + convertLuctoriosFormatToHtml(this.message) + '</b></label>',
      1, 1, 'width:100%;text-align:center;')
    if ((this.code === FAILURE) || (this.code === CRITIC) || (this.code === GRAVE)) {
      if (this.stackText !== '') {
        titles.push(Singleton().getTranslate('Call-stack'))
        contents.push('<pre>' + this.stackText + '</pre>')
      }
      extraId = contents.length
      titles.push('Extra')
      contents.push('<label>' + this.type + '</label>')
      if (this.requette !== '') {
        titles.push(Singleton().getTranslate('Requette'))
        contents.push('<pre>' + this.getInfo(this.requette) + '</pre>')
      }
      if (this.reponse !== '') {
        rep = this.reponse
        pos = rep.indexOf('?>')
        if (pos >= 0) {
          rep = rep.substring(pos + 2)
        }
        pos = rep.indexOf('<REPONSES')
        if (pos >= 0) {
          if (pos > 0) {
            contents[extraId] = rep.substring(0, pos - 1).trim()
          }
          titles.push(Singleton().getTranslate('Reponse'))
          contents.push('<pre>' + this.getInfo(rep.substring(pos)) + '</pre>')
        } else {
          contents[extraId] = rep.trim()
        }
      }
      table[1] = []
      var brnInfo = '<input type=\'button\' name=\'info\' value=\'>>\'/>'
      var brnSend = ''
      if (Singleton().mDesc !== null) {
        brnSend = '<input type=\'button\' name=\'send\' value=\'' + Singleton().getTranslate('Sent to support') + '\'/>'
      }
      table[1][0] = new CompBasic(brnInfo + brnSend, 2, 1, 'text-align:center;')
      table[2] = []
      table[2][0] = new CompBasic(createTab(titles, contents), 2, 1)
    }
    self = this
    this.mGUI = new GUIManage(this.getId(), errTitle, null)

    if (GMultiServer === true) {
      acts[0] = new ActionInt()
      acts[0].initializeEx(null, null, Singleton().getTranslate('Servers'))
      acts[0].mIcon = 'images/status.png'
      acts[0].callback = gConfigServers
      extraId = 1
    } else {
      extraId = 0
    }
    acts[extraId] = new ActionInt()
    acts[extraId].initializeEx(null, null, Singleton().getTranslate('Close'))
    acts[extraId].mIcon = 'images/close.png'
    acts[extraId].callback = $.proxy(this.mGUI.close, this.mGUI)

    this.mGUI.addcontent(createTable(table), acts)
    this.mGUI.showGUI(true)
    comp = this.mGUI.getHtmlDom()
    currentGui = this.mGUI
    comp.find('input[name=\'info\']').click(function () {
      if ($(this).attr('value') === '>>') {
        $(this).attr('value', '<<')
        comp.find('table:eq(0) > tbody > tr:eq(2) > td:eq(0)').show()
      } else {
        $(this).attr('value', '>>')
        comp.find('table:eq(0) > tbody > tr:eq(2) > td:eq(0)').hide()
      }
      currentGui.moveCenter()
    })
    this.mGUI.getHtmlDom().find('input[name=\'send\']').click(function () {
      window.location = self.sendSupport()
    })
    comp.find('table:eq(0) > tbody > tr:eq(2) > td:eq(0)').hide()
    this.mGUI.moveCenter()
    jcnt = this.mGUI.getHtmlDom()
    jcnt[0].style.height = (jcnt[0].clientHeight + 10) + 'px'
    jcnt[0].style.width = (jcnt[0].clientWidth + 5) + 'px'
  }

  sendSupport () {
    var complement = Singleton().getTranslate('Describ your problem.<br>Thanks<br><br>')
    complement += '<h1>' + this.message + '</h1>'
    if (this.stackText !== '') {
      complement += this.stackText + '<br><br>'
    }
    return Singleton().mDesc.fillEmailSupport(Singleton().getTranslate('Bug report'), complement)
  }
}

export var alertFunction = function (message) {
  var obs = new ObserverException()
  obs.setContent({
    'exception': {
      'message': message,
      'code': IMPORTANT,
      'debug': '',
      'type': '',
      'requette': '',
      'reponse': ''
    }
  })
  obs.show('alert')
}

window.onerror = function myErrorHandler (errorMsg, source, lineno, columnNo, error) {
  var errorDesc
  var stack
  var obs
  var typeError
  var errname
  stack = source + '->' + lineno + ':' + columnNo
  if (error !== undefined) {
    if (error.type !== undefined) {
      typeError = error.type
      errname = 'LucteriosException'
      errorDesc = []
      errorDesc[0] = error.message
      errorDesc[1] = error.info
      if (error.extra !== undefined) {
        errorDesc[2] = error.extra.toString()
      }
      if (error.fileName !== undefined) {
        stack = error.fileName + ':' + error.lineNumber + ':' + error.columnNumber
      }
    } else {
      typeError = FAILURE
      errname = error.name
      errorDesc = []
      errorDesc[0] = error.message
      errorDesc[1] = '*'
      stack = error.stack
    }
  } else {
    errorDesc = []
    errorDesc[0] = errorMsg
    stack = source + '->' + lineno + ':' + columnNo
    typeError = FAILURE
  }
  errorDesc[1] = errorDesc[1] ? encodeURIComponent(errorDesc[1]) : ''
  errorDesc[2] = errorDesc[2] ? encodeURIComponent(errorDesc[2]) : ''
  obs = new ObserverException()
  obs.setContent({
    'exception': {
      'message': errorDesc[0],
      'code': typeError,
      'debug': stack,
      'type': errname,
      'requette': errorDesc[1],
      'reponse': errorDesc[2]
    }
  })
  obs.show('Exception')
  return false
}
