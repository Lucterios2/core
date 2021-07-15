'use strict'
/* global Camera, FileReader */
import { LucteriosException, CRITIC, IMPORTANT, MINOR, postLog, unusedVariables, convertLuctoriosFormatToHtml, lpad } from './utils.js'
import { Singleton } from './singleton.js'
import { SELECT_NONE, SELECT_SINGLE, SELECT_MULTI } from './action.js'
import { CompBasic, formatToString } from './gui.utils.js'
const $ = require('jquery')
const util = require('util')
const atob = require('atob')
const JSZip = require('jszip')
global.$ = $
global.util = util
global.Singleton = Singleton

var tinymce
if (screen.istest === undefined) {
  tinymce = require('tinymce')
} else {
  tinymce = {
    init: function () {},
    get: function () { return '' }
  }
}

export const NULL_VALUE = 'NULL'

export class CompGeneric extends CompBasic {
  constructor (aOwner) {
    super()
    this.name = ''
    this.VMin = 0
    this.HMin = 0
    this.tab = 0
    this.description = ''
    this.tag = ''
    this.descComp = null
    this.owner = aOwner
  }

  getIdent () {
    return util.format('%s_%s', this.owner.getId(), this.name)
  }

  getGUIComp () {
    return $('#' + this.owner.getId()).find(util.format('%s[name=\'%s\']:eq(0)', this.tag, this.name))
  }

  setEnabled (isEnabled) {
    this.getGUIComp().prop('disabled', !isEnabled)
    if (this.descComp !== null) {
      this.descComp.setEnabled(isEnabled)
    }
  }

  setVisible (isVisible) {
    var cellCont = this.getGUIComp()[0]
    while ((cellCont.nodeName !== 'TD') && (cellCont.parentNode !== null) && (cellCont.parentNode !== cellCont)) {
      cellCont = cellCont.parentNode
    }
    if (cellCont.style !== null) {
      if (isVisible) {
        cellCont.style.display = null
        cellCont.style.fontSize = null
      } else {
        cellCont.style.display = 'none'
        cellCont.style.fontSize = '0px'
      }
    }
    if (this.descComp !== null) {
      this.descComp.setVisible(isVisible)
    }
  }

  requestFocus () {
    this.getGUIComp().focus()
  }

  getValue () {
    return this.getGUIComp().val()
  }

  initialVal () {
    return null
  }

  setValue (jsonvalue) {
    this.initial(jsonvalue)
    this.getGUIComp().val(this.initialVal())
  }

  initial (component) {
    if (this.name === '') {
      this.name = component.name
      this.description = component.description || ''
      this.description = this.description.replace(/%E9/g, 'é').replace(/%E8/g, 'è').replace(/%EA/g, 'ê')
      this.description = this.description.replace(/%[D-F][0-9A-F]/g, '?')
      this.tab = component.tab
      this.x = component.x
      this.y = component.y
      this.vmin = parseInt(component.VMin, 10) || -1
      this.hmin = parseInt(component.HMin, 10) || -1
      this.colspan = component.colspan
      this.rowspan = component.rowspan
      this.needed = component.needed
      this.isNull = !this.needed && (component.value === NULL_VALUE)
    }
  }

  getAttribHtml (args, isJustify) {
    args.name = this.name
    args.id = this.getIdent()
    args.description = this.description
    if (args.cssclass === undefined) {
      args.cssclass = ''
    }
    args.cssclass += ' classControle'
    if (isJustify) {
      args.cssclass += ' lctjustify'
    }
    if (this.hmin !== -1) {
      if (args.style === undefined) {
        args.style = ''
      }
      args.style += util.format('min-width: %spx;', this.hmin)
    }
    if (this.vmin !== -1) {
      if (args.style === undefined) {
        args.style = ''
      }
      args.style += util.format('min-height: %spx;', this.vmin)
    }
    var html = ''
    var element
    for (element in args) {
      if (args.hasOwnProperty(element)) {
        html += util.format(' %s=\'%s\'', element.replace('cssclass', 'class'), args[element])
      }
    }
    return html
  }

  getHtml () {
    var html = '<lct-cell>'
    if (this.description !== '') {
      html += util.format('<label for=\'%s\'>', this.getIdent())
      html += this.description
      html += '</label>'
      html += '<lct-ctrl>'
      html += this.getSubHtml()
      html += '</lct-ctrl>'
    } else {
      html += this.getSubHtml()
    }
    html += '</lct-cell>'
    return html
  }

  getBuildHtml (args, isJustify, isClose) {
    var html = '<' + this.tag + this.getAttribHtml(args, isJustify)
    if (isClose) {
      html += '/'
    }
    html += '>'
    return html
  }

  checkValid () {
    var msgText
    if (this.needed && ((this.getValue() === null) || (this.getValue() === ''))) {
      msgText = Singleton().getTranslate('This field is needed!')
      if (this.description.length > 0) {
        msgText = Singleton().getTranslate('The field \'%s\' is needed!').format(decodeURIComponent(this.description.replace(/\+/g, ' ')))
      }
      throw new LucteriosException(MINOR, msgText)
    }
  }

  fillValue (params) {
    if (this.initialVal() !== null) {
      params.put(this.name, this.getValue())
    }
  }

  addAction () {
    return undefined
  }

  guiFinalize () {
  }
}

// image
export class CompImage extends CompGeneric {
  initial (component) {
    super.initial(component)
    this.height = component.height
    this.width = component.width
    this.src = component.value || ''
    this.type = component.type || ''
    this.needed = 0
    this.tag = 'img'
  }

  checkValid () {
  }

  getSubHtml () {
    var srcImg = this.src
    if (this.type === '') {
      srcImg = Singleton().Transport().getIconUrl(this.src + '?val=' + Math.floor(Math.random() * 1000))
    } else {
      if (this.src.substring(0, 10) === 'data:image') {
        srcImg = this.src
      } else {
        srcImg = util.format('data:image/%s;base64,%s', this.type, this.src)
      }
    }
    return this.getBuildHtml({ 'src': srcImg }, false, true)
  }
}

// label formaté
export class CompLabelForm extends CompGeneric {
  initial (component) {
    super.initial(component)
    this.label = ''
    this.needed = 0
    this.value = component.value
    this.formatnum = component.formatnum || ''
    this.formatstr = component.formatstr || '%s'
    this.formatstr = this.formatstr.replace(/%s/g, '%s')
    this.tag = 'span'
  }

  checkValid () {
  }

  getSubHtml () {
    var label = formatToString(this.value, this.formatnum, this.formatstr)
    return this.getBuildHtml({}, false, false) + convertLuctoriosFormatToHtml(label) + '</span>'
  }
}

export class CompCaptcha extends CompGeneric {
  initial (component) {
    super.initial(component)
    this.tag = 'input'
    this.num1 = Math.floor((Math.random() * 10) + 1)
    this.num2 = Math.floor((Math.random() * 10) + 1)
    this.operation = Math.floor((Math.random() * 3) + 1)
    if (this.operation === 0) {
      this.total = this.num1 + this.num2
      this.operationTxt = '+'
    } else if ((this.operation === 1) && (this.num2 < this.num1)) {
      this.total = this.num1 - this.num2
      this.operationTxt = '-'
    } else {
      this.total = this.num1 * this.num2
      this.operationTxt = 'x'
    }
  }

  getSubHtml () {
    var args = { type: 'text', cssclass: 'lctcapcha' }
    args.value = ''
    return util.format('%s %s %s = %s', this.num1, this.operationTxt, this.getBuildHtml(args, false, true), this.total)
  }

  initialVal () {
    return this.value
  }

  checkValid () {
    super.checkValid()
    var msgText
    var inputVal = parseInt('0' + this.getGUIComp().val(), 10)
    if (inputVal !== this.num2) {
      msgText = Singleton().getTranslate('Captcha wrong!')
      throw new LucteriosException(MINOR, msgText)
    }
  }
}

// event
export class CompAbstractEvent extends CompGeneric {
  initial (component) {
    super.initial(component)
    if (component.action) {
      this.action = Singleton().CreateAction()
      this.action.initialize(this.owner, Singleton().Factory(), component.action)
      this.action.setCheckNull(false)
    } else {
      this.action = null
    }
    this.javaScriptContent = component.javascript || ''
    if (component.isDefault) {
      this.owner.mDefaultBtn = util.format('%s[name=\'%s\']', this.tag, this.name)
    }
  }

  addAction () {
    return undefined
  }

  getActFunction () {
    var actFunction = null
    var adder = null
    var initVal
    if ((this.javaScriptContent !== '') || (this.action !== null)) {
      postLog('java script :' + this.javaScriptContent)
      actFunction = function async () {
        if (this.javaScriptContent !== '') {
          adder = new Function('current', 'parent', 'Singleton', this.javaScriptContent) // eslint-disable-line no-new-func
          adder(this, this.owner, Singleton)
        }
        if (this.action !== null) {
          if (this.isNull === true) {
            initVal = NULL_VALUE
          } else {
            initVal = this.initialVal()
          }
          if (this.getValue() !== initVal) {
            this.action.actionPerformed()
          }
        }
      }
      if (this.javaScriptContent !== '') {
        adder = new Function('current', 'parent', 'Singleton', this.javaScriptContent) // eslint-disable-line no-new-func
        adder(this, this.owner, Singleton)
      }
    }
    return actFunction
  }

  addActionEx (typeAct) {
    var actFunction = this.getActFunction()
    var guiComp
    if (actFunction !== null) {
      guiComp = this.getGUIComp()
      switch (typeAct) {
        case 0: // focus
          guiComp.focusout($.proxy(actFunction, this))
          break
        case 1: // click
          guiComp.click($.proxy(actFunction, this))
          break
        case 2: // change
          guiComp.change($.proxy(actFunction, this))
          break
        default:
          throw new LucteriosException(CRITIC, 'Bad type!')
      }
    }
    this.addActionNull(actFunction)
  }

  addActionNull (actFunction) {
    var nullcheck
    if (this.needed === false) {
      nullcheck = $('#' + this.owner.getId()).find(util.format('input[name=\'nullcheck_%s\']:eq(0)', this.name))
      nullcheck.change($.proxy(function () {
        if (actFunction !== null) {
          $.proxy(actFunction, this)()
        }
        this.setEnabled(!nullcheck[0].checked)
      }, this))
      if (this.isNull) {
        this.setEnabled(false)
      }
    }
  }

  addnullcheck () {
    var res = ''
    var valcheck = ''
    if (this.needed === false) {
      if (this.isNull === true) {
        valcheck = 'checked = \'checked\''
      }
      res = util.format('<input class=\'class_checknull\' type=\'checkbox\' name=\'nullcheck_%s\' %s/>', this.name, valcheck)
    }
    return res
  }

  isReturnNull () {
    var res = false
    var nullcheck
    if (this.needed === false) {
      nullcheck = $('#' + this.owner.getId()).find(util.format('input[name=\'nullcheck_%s\']:eq(0)', this.name))
      res = nullcheck[0].checked
    }
    return res
  }
}

// bouton
export class CompButton extends CompAbstractEvent {
  initial (component) {
    super.initial(component)
    this.isMini = component.is_mini
    this.needed = 0
    this.tag = 'button'
    this.clickName = ''
    this.clickValue = ''
    this.hasBeenClicked = false
    this.notifyPerformed = null
    this.btnaction = null
  }

  async actionPerformed () {
    this.hasBeenClicked = true
    if (this.notifyPerformed !== null) {
      await this.notifyPerformed()
    }
    await this.btnaction.actionPerformed()
    this.hasBeenClicked = false
  }

  addAction () {
    this.addActionEx(1)
  }

  checkValid () {

  }

  getSubHtml () {
    if (this.action !== null) {
      var arg = {}
      var title
      var btnIcon
      var htmltagImgbegin
      this.btnaction = this.action
      this.action = this
      if (this.isMini) {
        arg.cssclass = 'lctbtnmini'
      } else {
        arg.cssclass = 'lctbtn'
      }
      if (!this.isMini || (this.btnaction.getIcon() === '')) {
        title = this.btnaction.getTitle()
        htmltagImgbegin = '<img src=\'%s\' style=\'max-width:22px\'/>'
      } else {
        title = ''
        htmltagImgbegin = '<img src=\'%s\' style=\'max-width:22px\' title=\'' + this.btnaction.getTitle() + '\'/>'
      }
      if (this.btnaction.getIcon() !== '') {
        btnIcon = Singleton().Transport().getIconUrl(this.btnaction.getIcon())
        title = util.format(htmltagImgbegin, btnIcon) + title
      }
      return this.getBuildHtml(arg, false, false) + title + '</button>'
    }
    return ''
  }

  setSelectType (aSelectType) {
    var enabled = false
    switch (aSelectType) {
      case SELECT_NONE:
        enabled = (this.btnaction.mSelect === SELECT_NONE)
        break
      case SELECT_SINGLE:
        enabled = true
        break
      case SELECT_MULTI:
        enabled = (this.btnaction.mSelect !== SELECT_SINGLE)
        break
      default:
        throw new LucteriosException(CRITIC, 'Bad type!')
    }
    this.setEnabled(enabled)
  }
}

// case à cocher
export class CompCheck extends CompAbstractEvent {
  initial (component) {
    super.initial(component)
    var val = component.value
    this.checked = (parseInt(val, 10) === 1) || (val === 'o')
    this.tag = 'input'
  }

  getSubHtml () {
    var args = {
      'type': 'checkbox'
    }
    if (this.checked) {
      args.checked = 'checked'
    }
    return this.getBuildHtml(args, false, true)
  }

  getValue () {
    var comp = this.getGUIComp()
    return comp[0].checked
  }

  setValue (jsonvalue) {
    this.initial(jsonvalue)
    this.getGUIComp()[0].checked = this.initialVal()
  }

  initialVal () {
    return this.checked
  }

  checkValid () {
  }

  fillValue (params) {
    if (this.getValue()) {
      params.put(this.name, 'o')
    } else {
      params.put(this.name, 'n')
    }
  }

  addAction () {
    this.addActionEx(2)
  }
}

export class CompLink extends CompGeneric {
  initial (component) {
    super.initial(component)
    this.label = convertLuctoriosFormatToHtml(component.value)
    this.link = component.link
    this.needed = 0
    this.tag = 'a'
  }

  checkValid () {
  }

  getSubHtml () {
    return this.getBuildHtml({ href: this.link, target: '_blank' }, false, false) + this.label + '</a>'
  }
}

export class CompEdit extends CompAbstractEvent {
  initial (component) {
    super.initial(component)
    var regex
    this.value = component.value
    this.size = component.size || -1
    regex = component.reg_expr
    if (regex !== '') {
      this.mask = new RegExp(regex, 'i')
    } else {
      this.mask = null
    }
    this.tag = 'input'
  }

  getSubHtml () {
    var args = {
      'type': 'text'
    }
    args.value = this.initialVal()
    return this.getBuildHtml(args, true, true)
  }

  initialVal () {
    return this.value
  }

  checkValid () {
    super.checkValid()
    var msgText
    var inputVal
    if (this.mask !== null) {
      inputVal = this.getGUIComp().val()
      if (!this.mask.test(inputVal)) {
        msgText = Singleton().getTranslate('Invalid format!')
        throw new LucteriosException(MINOR, msgText)
      }
    } else if (this.size !== -1) {
      inputVal = this.getGUIComp().val().trim()
      if (inputVal.length > this.size) {
        msgText = Singleton().getTranslate('Size too long!')
        throw new LucteriosException(MINOR, msgText)
      }
    }
  }

  addAction () {
    this.addActionEx(0)
    if ((this.mask !== null) || (this.size !== -1)) {
      this.getGUIComp().keyup($.proxy(function () {
        var inputVal = this.getGUIComp().val()
        if (((this.mask !== null) && !this.mask.test(inputVal)) || ((this.size !== -1) && (inputVal.trim().length > this.size))) {
          this.getGUIComp().css({
            'background-color': 'red',
            'color': 'black'
          })
        } else {
          this.getGUIComp().removeAttr('style')
        }
      }, this))
    }
  }
}

export class CompFloat extends CompAbstractEvent {
  initial (component) {
    super.initial(component)
    var textValue = ''
    var nbDec = (component.prec || 0)
    var decI
    if (this.isNull === false) {
      textValue = component.value
    }
    if (textValue === '') {
      textValue = '0'
    }
    this.value = parseFloat(textValue)
    this.min = component.min ? parseFloat(component.min) : 0.0
    this.max = component.max ? parseFloat(component.max) : 1000.0
    this.prec = 1
    for (decI = 0; decI < nbDec; decI++) {
      this.prec = this.prec / 10
    }
    this.tag = 'input'
  }

  getSubHtml () {
    var args = {
      'type': 'text'
    }
    args.value = this.initialVal()
    return this.addnullcheck() + this.getBuildHtml(args, true, true)
  }

  getValue () {
    var valNum
    if (this.isReturnNull() === true) {
      return NULL_VALUE
    }
    valNum = this.getGUIComp().val()
    valNum = valNum.replace(',', '.').replace(/[^0-9.-]/g, '')
    if (isNaN(valNum)) {
      valNum = 0
    }
    valNum = Math.max(valNum, this.min)
    valNum = Math.min(valNum, this.max)
    return util.format('%s', valNum)
  }

  initialVal () {
    return util.format('%s', this.value)
  }

  setEnabled (isEnabled) {
    try {
      if (isEnabled === true) {
        this.getGUIComp().spinner('enable')
      } else {
        this.getGUIComp().spinner('disable')
      }
    } catch (lctept) {
      this.getGUIComp().prop('disabled', !isEnabled)
    }
  }

  addAction () {
    this.getGUIComp().spinner({ step: this.prec, min: this.min, max: this.max, numberFormat: 'n' })
    this.addActionEx(0)
  }
}

class EditorMenu {
  constructor (ownerId, selector, aSubMenu, callback) {
    var isubMenu, subMenu
    this.ownerId = ownerId
    this.selector = selector
    if (callback) {
      this.callback = callback
    } else {
      this.callback = $.proxy(this.defaultCallback, this)
    }
    this.submenus = {}
    for (isubMenu = 0; isubMenu < aSubMenu.length; isubMenu++) {
      subMenu = aSubMenu[isubMenu]
      this.submenus[subMenu[1]] = { name: subMenu[0] }
    }
  }

  getGUIComp () {
    return $('#' + this.ownerId).find(this.selector)
  }

  addMenuAction () {
    if (Object.keys(this.submenus).length > 0) {
      $('#' + this.ownerId).contextMenu({ selector: this.selector, items: this.submenus, callback: this.callback })
    }
  }

  defaultCallback (key, options) {
    unusedVariables(options)
    var cursorPos, valArea, variableText, textBefore, textAfter
    variableText = '#' + key
    cursorPos = this.getGUIComp().prop('selectionStart')
    valArea = this.getGUIComp().val()
    textBefore = valArea.substring(0, cursorPos)
    textAfter = valArea.substring(cursorPos, valArea.length)
    this.getGUIComp().val(textBefore + variableText + textAfter)
  }
}

export class CompMemo extends CompAbstractEvent {
  initial (component) {
    super.initial(component)
    this.value = component.value.replace(/\{\[newline\]\}/g, '\n').replace(/\{\[br\/\]\}/g, '\n')
    this.withHypertext = component.with_hypertext
    this.tag = 'textarea'
    this.submenu = component.submenu
    this.isFocused = false
    this.editro = null
  }

  getSubHtml () {
    var isubMenu
    var subMenu
    var html = ''
    var attrib = {}
    if (this.withHypertext) {
      attrib = { style: 'min-width: 600px;min-height: 240px;' }
    }
    html += util.format('<textarea \'%s\'>%s</textarea>', this.getAttribHtml(attrib, true), this.initialVal())
    if (this.withHypertext && (this.submenu.length > 0)) {
      html += util.format('<ul id=\'menu_%s\' style=\'width: 30px\'>', this.getIdent())
      html += '<li>'
      html += '<div>+</div>'
      html += '<ul>'
      for (isubMenu = 0; isubMenu < this.submenu.length; isubMenu++) {
        subMenu = this.submenu[isubMenu]
        html += util.format('<li value=\'%s\'><div>%s</div></li>', subMenu[1], subMenu[0])
      }
      html += '</ul>'
      html += '</li>'
      html += '</ul>'
    }
    return html
  }

  initialVal () {
    var value = this.value
    if (this.withHypertext) {
      value = convertLuctoriosFormatToHtml(value)
    }
    return value
  }

  getAttribHtml (args, isJustify) {
    var html = ''
    var element
    if (this.withHypertext) {
      args.id = this.getIdent()
      for (element in args) {
        if (args.hasOwnProperty(element)) {
          html += util.format(' %s=\'%s\'', element, args[element])
        }
      }
    } else {
      html = super.getAttribHtml(args, isJustify)
    }
    return html
  }

  fillValue (params) {
    var val
    if (this.withHypertext) {
      val = tinymce.get(this.getIdent()).getContent()
      params.put(this.name, val.replace(/\n/g, '{[br/]}').replace(/</g, '{[').replace(/>/g, ']}'))
    } else {
      val = this.getValue()
      params.put(this.name, val.replace(/\n/g, '{[br/]}'))
    }
  }

  checkValid () {
    if (this.isFocused) {
      throw new LucteriosException(MINOR, '')
    }
    super.checkValid()
  }

  addAction () {
    var self = this
    this.addActionEx(0)
    if (this.withHypertext) {
      tinymce.init({
        selector: '#' + this.getIdent()
      })
    }
    if (this.withHypertext && (this.submenu.length > 0)) {
      $(util.format('#menu_%s', this.getIdent())).menu({
        select (event, ui) {
          unusedVariables(event)
          var text, value
          value = ui.item[0].attributes.value
          if (value) {
            text = $('#' + self.getId()).val()
            $('#' + self.getId()).jqteVal(text + '#' + value.nodeValue)
          }
        }
      })
    }
  }
}

class EditorHypertext {
  constructor (aOwnerId, aName) {
    this.ownerId = aOwnerId
    this.name = aName
  }
  getSubHtml (attribut, value) {
    var html = ''
    html += '<div class=\'ui-widget-header\'>'
    html += util.format('<img id=\'bold_%s\' src=\'images/bold.png\' class=\'memobtn\'>', this.name)
    html += util.format('<img id=\'italic_%s\' src=\'images/italic.png\' class=\'memobtn\'>', this.name)
    html += util.format('<img id=\'underline_%s\' src=\'images/underline.png\' class=\'memobtn\'>', this.name)
    html += util.format('<img id=\'black_%s\' src=\'images/black.png\' class=\'memobtn\'>', this.name)
    html += util.format('<img id=\'blue_%s\' src=\'images/blue.png\' class=\'memobtn\'>', this.name)
    html += util.format('<img id=\'red_%s\' src=\'images/red.png\' class=\'memobtn\'>', this.name)
    html += util.format('<img id=\'green_%s\' src=\'images/green.png\' class=\'memobtn\'>', this.name)
    html += '</div>'
    html += '<textarea ' + attribut + '>' + value + '</textarea>'
    return html
  }
  addEditorAction () {
    var self = this
    $(util.format('#bold_%s', this.name)).click(function () {
      self.addTextTag('b', '')
    })
    $(util.format('#italic_%s', this.name)).click(function () {
      self.addTextTag('i', '')
    })
    $(util.format('#underline_%s', this.name)).click(function () {
      self.addTextTag('u', '')
    })
    $(util.format('#black_%s', this.name)).click(function () {
      self.addTextTag('font', 'color=\'black\'')
    })
    $(util.format('#red_%s', this.name)).click(function () {
      self.addTextTag('font', 'color=\'red\'')
    })
    $(util.format('#blue_%s', this.name)).click(function () {
      self.addTextTag('font', 'color=\'blue\'')
    })
    $(util.format('#green_%s', this.name)).click(function () {
      self.addTextTag('font', 'color=\'green\'')
    })
  }

  getGUIComp () {
    return $('#' + this.ownerId).find('textarea[name=\'%s\']:eq(0)'.format(this.name))
  }

  addTextTag (tagname, extra) {
    var cursorPosBegin, cursorPosEnd, valArea, selectVal, textBefore, textAfter
    if (extra !== '') {
      extra = ' ' + extra
    }
    cursorPosBegin = this.getGUIComp().prop('selectionStart')
    cursorPosEnd = this.getGUIComp().prop('selectionEnd')
    valArea = this.getGUIComp().val()
    textBefore = valArea.substring(0, cursorPosBegin)
    selectVal = valArea.substring(cursorPosBegin, cursorPosEnd)
    textAfter = valArea.substring(cursorPosEnd, valArea.length)
    this.getGUIComp().val(util.format('%s{[%s%s]}%s{[/%s]}%s', textBefore, tagname, extra, selectVal, tagname, textAfter))
  }
}

export class CompXML extends CompAbstractEvent {
  initial (component) {
    super.initial(component)
    this.value = component.value
    this.editor = new EditorHypertext(this.owner.getId(), this.name)
    this.menu = new EditorMenu(this.owner.getId(), util.format('textarea[name=\'%s\']:eq(0)', this.name), component.submenu)
    this.tag = 'textarea'
  }

  getSubHtml () {
    return this.editor.getSubHtml(this.getAttribHtml({}, true), this.initialVal())
  }

  initialVal () {
    return this.value
  }

  fillValue (params) {
    var val = this.getValue()
    params.put(this.name, val)
  }

  addAction () {
    this.addActionEx(0)
    this.editor.addEditorAction()
    this.menu.addMenuAction()
  }
}

export class CompPassword extends CompAbstractEvent {
  initial (component) {
    super.initial(component)
    this.value = component.value
    this.security = component.security || 0
    this.tag = 'input'
  }

  getSubHtml () {
    var args = {
      'type': 'password'
    }
    args.value = this.initialVal()
    return this.getBuildHtml(args, true, true)
  }

  initialVal () {
    return this.value
  }

  checkValid () {
    super.checkValid()
    if ((this.security !== 0) && !this.getGUIComp().prop('disabled')) {
      var msgText
      var inputVal
      var lowerreg = /^(?=.*[a-z]).+$/
      var upperreg = /^(?=.*[A-Z]).+$/
      var noalphareg = /^(?=.*[0-9_\W]).+$/
      inputVal = this.getGUIComp().val()
      if (inputVal.length < 6) {
        msgText = Singleton().getTranslate('Password too short!')
        throw new LucteriosException(MINOR, msgText)
      }
      if (!lowerreg.test(inputVal) || !upperreg.test(inputVal) || !noalphareg.test(inputVal)) {
        msgText = Singleton().getTranslate('Password too simple!')
        throw new LucteriosException(MINOR, msgText)
      }
    }
  }

  addAction () {
    this.addActionEx(0)
  }
}

export class CompDate extends CompAbstractEvent {
  initial (component) {
    super.initial(component)
    if (this.isNull === false) {
      this.value = component.value || ''
    } else {
      this.value = ''
    }
    if (this.value === '') {
      var today = new Date()
      this.value = util.format('%s-%s-%s', today.getFullYear(), lpad((today.getMonth() + 1).toString(), '0', 2), lpad(today.getDate().toString(), '0', 2))
    }
    this.tag = 'input'
  }

  getSubHtml () {
    var args = { 'type': 'text', 'cssclass': 'datepicker' }
    var dateNums = this.initialVal().split('-')
    args.value = util.format('%s/%s/%s', dateNums[2], dateNums[1], dateNums[0])
    if (this.needed === false) {
      args.cssclass += ' lctdateneeded'
    } else {
      args.cssclass += ' lctdate'
    }
    return this.addnullcheck() + this.getBuildHtml(args, false, true)
  }

  getValue () {
    var dateNums
    if (this.isReturnNull() === true) {
      return NULL_VALUE
    }
    dateNums = this.getGUIComp().val().split('/')
    return util.format('%s-%s-%s', dateNums[2], dateNums[1], dateNums[0])
  }

  setValue (jsonvalue) {
    this.initial(jsonvalue)
    var dateNums = this.initialVal().replace(/\//g, '-').split('-')
    this.getGUIComp().val(util.format('%s/%s/%s', dateNums[2], dateNums[1], dateNums[0]))
  }

  initialVal () {
    return this.value
  }

  addAction () {
    this.addActionEx(2)
  }
}

export class CompTime extends CompAbstractEvent {
  initial (component) {
    super.initial(component)
    if (this.isNull === false) {
      this.value = component.value
    }
    if (this.value === '') {
      var today = new Date()
      this.value = util.format('%s:%s', lpad(today.getHours().toString(), '0', 2), lpad(today.getMinutes().toString(), '0', 2))
    }
    this.tag = 'input'
  }

  getValue () {
    if (this.isReturnNull() === true) {
      return NULL_VALUE
    }
    return super.getValue()
  }

  getSubHtml () {
    var args = {
      'type': 'text',
      'class': 'timespinner'
    }
    args.value = this.initialVal()
    return this.addnullcheck() + this.getBuildHtml(args, true, true)
  }

  setEnabled (isEnabled) {
    if (this.descComp !== null) {
      this.descComp.setEnabled(isEnabled)
    }
  }

  initialVal () {
    return this.value
  }

  addAction () {
    this.addActionEx(0)
  }
}

export class CompDateTime extends CompAbstractEvent {
  initial (component) {
    super.initial(component)
    if (this.isNull === false) {
      this.value = component.value
    }
    if (this.value === '') {
      var today = new Date()
      this.value = util.format('%s-%s-%s %s:%s', today.getFullYear(), lpad((today.getMonth() + 1).toString(), '0', 2), lpad(today.getDate().toString(), '0', 2), lpad(today.getHours().toString(), '0', 2), lpad(today.getMinutes().toString(), '0', 2))
    }
    this.tag = 'input'
  }

  getGUICompTime () {
    return $('#' + this.owner.getId()).find(util.format('%s[name=\'%s\']:eq(1)', this.tag, this.name))
  }

  getSubHtml () {
    var dateTime = this.initialVal().split(' ')
    var dateNums = dateTime[0].split('-')
    var argsDt = {
      'type': 'text',
      'cssclass': 'datepicker lctdate'
    }
    var argsTm = {
      'type': 'text',
      'cssclass': 'timespinner lcttime'
    }
    argsDt.value = util.format('%s/%s/%s', dateNums[2], dateNums[1], dateNums[0])
    argsTm.value = dateTime[1]
    return this.addnullcheck() + this.getBuildHtml(argsDt, false, true) + this.getBuildHtml(argsTm, false, true)
  }

  initialVal () {
    return this.value
  }

  getValue () {
    var dateNums
    if (this.isReturnNull() === true) {
      return NULL_VALUE
    }
    dateNums = this.getGUIComp().val().split('/')
    return util.format('%s-%s-%s %s', dateNums[2], dateNums[1], dateNums[0], this.getGUICompTime().val())
  }

  setEnabled (isEnabled) {
    this.getGUIComp().prop('disabled', !isEnabled)
    if (this.descComp !== null) {
      this.descComp.setEnabled(isEnabled)
    }
  }

  setValue (jsonvalue) {
    this.initial(jsonvalue)
    var dateTime = this.initialVal().split(' ')
    var dateNums = dateTime[0].split('-')
    this.getGUIComp().val(util.format('%s/%s/%s', dateNums[2], dateNums[1], dateNums[0]))
    this.getGUICompTime().val(dateTime[1])
  }

  addAction () {
    var actFunction = this.getActFunction()
    if (actFunction !== null) {
      this.getGUIComp().change($.proxy(actFunction, this))
      this.getGUICompTime().focusout($.proxy(actFunction, this))
    }
    this.addActionNull(actFunction)
  }
}

class CompSelectCase {
  constructor (aOwner) {
    this.id = 0
    this.label = ''
    this.checked = false
  }

  initial (component) {
    this.id = component[0].toString()
    this.label = component[1]
    if (this.label === null) {
      this.label = '---'
    }
  }

  getSubHtml (value) {
    var html = '<option value=\'' + this.id + '\''
    if (((value !== null) && (value.toString() === this.id)) || ((value === null) && this.checked)) {
      html += ' selected'
    }
    html += '>' + this.label + '</option>'
    return html
  }
}

export class CompSelect extends CompAbstractEvent {
  initial (component) {
    super.initial(component)
    this.args = { cssclass: '' }

    // traitement des HEADER
    this.cases = []
    var iChild
    var cas
    component.case = component.case || []
    for (iChild = 0; iChild < component.case.length; iChild++) {
      cas = new CompSelectCase()
      cas.initial(component['case'][iChild])
      this.cases[this.cases.length] = cas
    }
    this.value = component.value
    if (this.value === undefined) {
      this.value = ''
    }
    this.tag = 'select'

    this.afterInitial(component)
  }

  afterInitial (component) {
    unusedVariables(component)
    if ((this.value === '') && (this.cases.length > 0)) {
      this.value = this.cases[0].id
    }
  }

  getOptionVal () {
    var html = ''
    var iHead
    for (iHead = 0; iHead < this.cases.length; iHead++) {
      html += this.cases[iHead].getSubHtml(this.value)
    }
    return html
  }

  getSubHtml () {
    var html = this.getBuildHtml(this.args, true, false)
    html += this.getOptionVal()
    html += util.format('</%s>', this.tag)
    return html
  }

  setValue (jsonvalue) {
    this.initial(jsonvalue)
    this.getGUIComp().html(this.getOptionVal())
  }

  initialVal () {
    return this.value
  }

  addAction () {
    this.addActionEx(2)
  }
}

export class CompCheckList extends CompSelect {
  afterInitial (component) {
    var iHead
    this.simple = parseInt(component.simple, 10) || 0
    this.args = {
      'cssclass': 'checklist'
    }
    if (!Array.isArray(this.value)) {
      this.value = []
    }
    this.args.multiple = 'multiple'
    if (this.simple === 2) {
      this.tag = 'span'
      this.args.cssclass = 'multiselect'
    }
    for (iHead = 0; iHead < this.cases.length; iHead++) {
      this.cases[iHead].checked = (this.value.indexOf(this.cases[iHead].id) !== -1)
    }
  }

  initialVal () {
    if (this.value.length === 0) {
      return ''
    }
    return this.value.join(';')
  }

  fillValue (params) {
    var res = this.getValue()
    if (res !== this.initialVal()) {
      params.put(this.name, res)
    }
  }

  getValue () {
    var res, iHead
    if (this.simple === 2) {
      res = []
      for (iHead = 0; iHead < this.cases.length; iHead++) {
        if (this.cases[iHead].checked) {
          res.push(this.cases[iHead].id)
        }
      }
    } else {
      res = this.getGUIComp().val()
    }
    if (res === null) {
      return ''
    }
    return res.join(';')
  }

  getOptionVal () {
    var html = ''
    var iHead
    if (this.simple !== 2) {
      for (iHead = 0; iHead < this.cases.length; iHead++) {
        html += this.cases[iHead].getSubHtml(null)
      }
    } else {
      html += '<lct-checklist>'
      html += util.format('<select name=\'%s_available\' multiple = \'multiple\'>', this.name)
      for (iHead = 0; iHead < this.cases.length; iHead++) {
        if (!this.cases[iHead].checked) {
          html += this.cases[iHead].getSubHtml(0)
        }
      }
      html += '</select>'
      html += '<div>'
      html += util.format('<button class=\'addall\' name=\'%s_addall\'><span class=\'fa fa-angle-double-right\'/></button>', this.name)
      html += util.format('<button class=\'add\' name=\'%s_add\'><span class=\'fa fa-angle-right\'/></button>', this.name)
      html += util.format('<button class=\'del\' name=\'%s_del\'><span class=\'fa fa-angle-left\'/></button>', this.name)
      html += util.format('<button class=\'delall\' name=\'%s_delall\'><span class=\'fa fa-angle-double-left\'/></button>', this.name)
      html += '</div>'
      html += util.format('<select name=\'%s_chosen\' multiple = \'multiple\'>', this.name)
      for (iHead = 0; iHead < this.cases.length; iHead++) {
        if (this.cases[iHead].checked) {
          html += this.cases[iHead].getSubHtml(0)
        }
      }
      html += '</select>'
      html += '</lct-checklist>'
    }
    return html
  }

  addAction () {
    if (this.simple === 1) {
      this.addActionEx(2)
    } else if (this.simple === 2) {
      this.getGUIComp().find(util.format('button[name=\'%s_addall\']:eq(0)', this.name)).click($.proxy(this.addallbtn, this))
      this.getGUIComp().find(util.format('button[name=\'%s_add\']:eq(0)', this.name)).click($.proxy(this.addbtn, this))
      this.getGUIComp().find(util.format('button[name=\'%s_del\']:eq(0)', this.name)).click($.proxy(this.delbtn, this))
      this.getGUIComp().find(util.format('button[name=\'%s_delall\']:eq(0)', this.name)).click($.proxy(this.delallbtn, this))
    } else {
      this.addActionEx(0)
    }
  }

  clickafterbtn () {
    var actFunction = this.getActFunction()
    this.getGUIComp().html(this.getOptionVal())
    this.addAction()
    if (actFunction !== null) {
      $.proxy(actFunction, this)()
    }
  }

  addallbtn () {
    var iHead
    for (iHead = 0; iHead < this.cases.length; iHead++) {
      this.cases[iHead].checked = true
    }
    this.clickafterbtn()
  }

  addbtn () {
    var iHead
    var valAvailable = this.getGUIComp().find(util.format('select[name=\'%s_available\']:eq(0)', this.name)).val()
    if (valAvailable !== null) {
      for (iHead = 0; iHead < this.cases.length; iHead++) {
        if (valAvailable.indexOf(this.cases[iHead].id) !== -1) {
          this.cases[iHead].checked = true
        }
      }
    }
    this.clickafterbtn()
  }

  delbtn () {
    var iHead
    var valChosen = this.getGUIComp().find(util.format('select[name=\'%s_chosen\']:eq(0)', this.name)).val()
    if (valChosen !== null) {
      for (iHead = 0; iHead < this.cases.length; iHead++) {
        if (valChosen.indexOf(this.cases[iHead].id) !== -1) {
          this.cases[iHead].checked = false
        }
      }
    }
    this.clickafterbtn()
  }

  delallbtn () {
    var iHead
    for (iHead = 0; iHead < this.cases.length; iHead++) {
      this.cases[iHead].checked = false
    }
    this.clickafterbtn()
  }
}

export class CompUpload extends CompGeneric {
  initial (component) {
    super.initial(component)
    this.filter = ''
    var filters = component.filter || []
    this.filter = filters.join(',')
    this.compress = component.compress
    this.httpFile = component.http_file
    this.maxsize = component.maxsize || 0
    this.withcam = component.withcam
    this.tag = 'input'
    this.selectedFile = null
    this.content = null
    this.contentIsloading = true
  }

  getSubHtml () {
    var html
    var args = {
      'type': 'file',
      'accept': this.filter,
      'style': 'opacity: 0;width:75%;'
    }
    html = '<div class=\'drop_zone\'>'
    html += '<button class=\'fileSelect\'>'
    html += util.format('<img src=\'%s\' title=\'%s\'/>', Singleton().Transport().getIconUrl('static/lucterios.CORE/images/open.png'),
      Singleton().getTranslate('File'))
    html += '</button>'
    if (this.withcam) {
      html += '<button class=\'cameraTakePicture\'>'
      html += util.format('<img src=\'%s\' title=\'%s\'/>', Singleton().Transport().getIconUrl('static/lucterios.CORE/images/camera.png'),
        Singleton().getTranslate('Picture'))
      html += '</button>'
    }
    html += '<img class=\'pictureToUpload\' style=\'display:none;\'></img>'
    html += '<div class=\'filename\'>---</div>'
    html += this.getBuildHtml(args, false, true)
    html += '<div>'
    html += Singleton().getTranslate('Drag one file to this zone ...')
    html += '</div>'
    html += '</div>'
    return html
  }

  addAction () {
    var guiComp = this.getGUIComp()
    guiComp.change($.proxy(this.fileselected, this))
    guiComp.parent().find('.fileSelect').click($.proxy(this.openfile, this))
    guiComp.parent().find('.cameraTakePicture').click($.proxy(this.cameraTakePicture, this))
  }

  openfile () {
    var guiComp = this.getGUIComp()
    guiComp.click()
  }

  fileselected () {
    var comp = this.getGUIComp()
    if (comp[0].files.length > 0) {
      this.selectedFile = comp[0].files[0]
    } else {
      this.selectedFile = null
    }
    this.getFileContentBase64()
  }

  getFileContentBase64 () {
    this.content = null
    this.content_isloading = true
    if (this.compress) {
      var self = this
      var zip = new JSZip()
      zip.file(this.name, this.getValue())
      zip.generateAsync({ type: 'blob' }).then(function (blobResult) {
        self.getEncodeFile(blobResult)
      })
    } else {
      this.getEncodeFile(this.getValue())
    }
  }

  getValue () {
    var filenameComp = this.getGUIComp().parent().find('.filename')
    var imageComp = this.getGUIComp().parent().find('.pictureToUpload')
    imageComp.prop('src', '')
    imageComp.css('display', 'none')
    if (this.selectedFile !== null) {
      filenameComp.text(this.selectedFile.name)
      if (this.selectedFile.type.split('/')[0] === 'image') {
        var reader = new FileReader()
        reader.onload = function (oEvent) {
          var imageData = new Image()
          imageData.src = oEvent.target.result
          imageData.onload = function () {
            var marginTop = (50 - (this.height * 50 / this.width)) / 2
            imageComp.css('margin-top', util.format('%spx', marginTop))
          }
          imageComp.prop('src', oEvent.target.result)
          imageComp.css('display', 'block')
        }
        reader.readAsDataURL(this.selectedFile)
      }
    } else {
      filenameComp.text('---')
    }
    return this.selectedFile
  }

  fillValue (params) {
    var fileToZip = this.getValue()
    if (fileToZip !== null) {
      if (this.contentIsloading) {
        throw new LucteriosException(MINOR, Singleton().getTranslate('Loading...'))
      }
      if (this.content !== null) {
        params.put(this.name, this.content)
        if (this.compress) {
          params.put(this.name + '_FILENAME', fileToZip.name)
        }
      }
    }
  }

  getEncodeFile (fileToSend) {
    var size
    var reader
    if (fileToSend.size > this.maxsize) {
      size = this.maxsize / (1024 * 1024)
      throw new LucteriosException(IMPORTANT, util.format(Singleton().getTranslate('Upload impossible<br/>The file must be less than %sMo '), size))
    }
    if (this.httpFile) {
      this.content = fileToSend
      this.contentIsloading = false
    } else {
      reader = new FileReader()
      reader.onload = $.proxy(function (readerEvt) {
        this.content = readerEvt.target.result
        this.contentIsloading = false
      }, this)
      reader.readAsDataURL(fileToSend)
    }
  }

  cameraTakePicture () {
    $('div.cordova-camera-capture').remove()
    navigator.camera.getPicture($.proxy(this.onCamSuccess, this), $.proxy(this.onCamFail, this), {
      quality: 50,
      destinationType: Camera.DestinationType.DATA_URI,
      encodingType: Camera.EncodingType.PNG,
      allowEdit: true,
      correctOrientation: true,
      cameraDirection: Camera.Direction.BACK
    })
  }

  onCamSuccess (imageData) {
    var bstr
    var imgSize
    var u8arr
    var imageName
    var today = new Date()
    imageName = util.format('image_%s-%s-%s_%s-%s.png', today.getFullYear(), lpad((today.getMonth() + 1).toString(), '0', 2), lpad(today.getDate().toString(), '0', 2), lpad(today.getHours().toString(), '0', 2), lpad(today.getMinutes().toString(), '0', 2))
    bstr = atob(imageData)
    imgSize = bstr.length
    u8arr = new Uint8Array(imgSize)
    while (imgSize--) {
      u8arr[imgSize] = bstr.charCodeAt(imgSize)
    }
    this.selectedFile = new File([ u8arr ], imageName, { type: 'image/png' })
    this.getFileContentBase64()
    $('div.cordova-camera-capture').remove()
  }

  onCamFail (error) {
    $('div.cordova-camera-capture').remove()
    if ((error !== undefined) && (error.message !== undefined)) {
      throw new LucteriosException(IMPORTANT, error.message)
    }
  }
}

export class CompDownload extends CompGeneric {
  initial (component) {
    super.initial(component)
    this.compress = component.compress
    this.httpFile = component.http_file
    this.maxsize = component.maxsize || 0
    this.fileName = component.value.trim()
    this.linkFileName = component.filename
    this.needed = 0
    this.tag = 'button'
  }

  checkValid () {

  }

  getSubHtml () {
    var args = { 'id': util.format('download_%s_%s', this.owner.getId(), this.name) }
    return '<label>' + this.fileName + '</label>' + this.getBuildHtml(args, false, false) + Singleton().getTranslate('Save as...') + '</button>'
  }

  addAction () {
    this.getGUIComp().click($.proxy(this.openFile, this))
  }

  openFile () {
    Singleton().Transport().getFileContent(this.linkFileName, $.proxy(this.receiveBlob, this))
  }

  async receiveBlob (blob) {
    if (this.compress && (blob.size !== 0)) {
      const zipFileLoaded = new JSZip()
      const self = this
      zipFileLoaded.loadAsync(blob.data).then(function (zip) {
        zip.forEach(function (relativePath, zipEntry) {
          zipEntry.async('base64').then(function (data) {
            Singleton().mFileManager.saveFile(data, self.fileName)
          })
        })
      })
    } else {
      Singleton().mFileManager.saveBlob(blob, this.fileName)
    }
  }
}
