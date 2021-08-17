'use strict'
import { unusedVariables, createGuid, postLog } from './utils.js'
import { Singleton } from './singleton.js'
const util = require('util')
const $ = require('jquery')

$(document).delegate('.ui-dialog', 'keyup', function (e) {
  var tagName = e.target.tagName.toLowerCase()
  tagName = (tagName === 'input' && e.target.type === 'button') ? 'button' : tagName
  if (e.which === $.ui.keyCode.ENTER && tagName !== 'textarea' && tagName !== 'select' && tagName !== 'button') {
    $(this).find('.ui-dialog-buttonset button').eq(0).trigger('click')
    return false
  }
})

export class GUIBasic {
  constructor (aId, aTitle, aCallback) {
    this.mId = aId
    this.mTitle = aTitle
    this.mCallback = aCallback
  }

  isExist () {
    var item = document.getElementById(this.mId)
    return (item !== null)
  }

  async close () {
    if (this.mCallback !== null) {
      await this.mCallback.close(true)
    } else {
      this.dispose()
    }
  }

  dispose () {
    if (document.getElementById(this.mId) !== null) {
      $('#' + this.mId).remove()
    }
  }

  getHtmlDom () {
    return $('#' + this.mId)
  }

  buildStruct (isModal) {
    unusedVariables(isModal)
  }

  correctStruct () {
    return undefined
  }

  buildFinal () {
    return undefined
  }

  showGUI (isModal) {
    var notExist = !this.isExist()
    var html = ''
    if (notExist) {
      html += util.format('<div id=\'%s\' title=\'%s\'>', this.mId, this.mTitle)
    }
    html += this.mHtmlBody
    if (notExist) {
      html += '</div>'
      $('#lucteriosClient').append(html)
      this.buildStruct(isModal)
    } else {
      $('#' + this.mId).html(html)
      this.correctStruct()
    }
    this.buildFinal()
  }

  setActive (aIsActive) {
    $('#' + this.mId).prop('disabled', !aIsActive)
    $(util.format('#%s .class_controle', this.mId)).prop('disabled', !aIsActive)
    if (aIsActive) {
      $('#' + this.mId).css('cursor', 'default')
    } else {
      $('#' + this.mId).css('cursor', 'progress')
    }
  }

  moveCenter () {
    var dlg = $('#' + this.mId).parent()
    var newLeft = (screen.width / 2) - (dlg.width() / 2)
    var newTop = (screen.height / 2) - (dlg.height() / 2)
    dlg.offset({
      top: newTop,
      left: newLeft
    })
  }
}

export class GUIManage extends GUIBasic {
  constructor (aId, aTitle, aCallback) {
    super(aId, aTitle, aCallback)
    this.mButtons = []
    this.withForm = false
    this.defaultbtn = ''
  }

  addcontent (aHtmlBody, aButtons) {
    if (this.withForm) {
      this.mHtmlBody = util.format('<form id=\'frm_%s\'>%s</form>', this.mId, aHtmlBody)
    } else {
      this.mHtmlBody = aHtmlBody
    }
    this.mButtons = aButtons
  }

  async actionClosePerformed () {
    if (this.mCallback !== null) {
      await this.mCallback.close(true)
    } else {
      $(this).dialog('close')
    }
  }

  getButtonList () {
    var buttonlist = []
    var iAct
    var newButton
    for (iAct = 0; iAct < this.mButtons.length; iAct += 1) {
      buttonlist[buttonlist.length] = this.mButtons[iAct].getButton()
    }

    if (buttonlist.length === 0) {
      newButton = {}
      newButton.text = Singleton().getTranslate('Close')
      newButton.click = $.proxy(this.actionClosePerformed, this)
      buttonlist = [ newButton ]
    }
    return buttonlist
  }

  buildStruct (isModal) {
    var args = {}
    var titlebar = null
    args = {
      title: this.mTitle,
      width: 'auto',
      height: 'auto',
      modal: isModal,
      classes: {
        'ui-dialog': 'lct-dialog',
        'ui-dialog-content': 'lct-dlgcontent',
        'ui-dialog-buttonpane': 'lct-dlgbtnpn',
        'ui-dialog-buttonset': 'lct-dlgbtnset'
      },
      resize: $.proxy(function (event, ui) {
        unusedVariables(event, ui)
        var tabid
        this.changeSizeChildreen()
        if ((this.mCallback !== null) && (this.mCallback.gui_finalize !== undefined)) {
          this.mCallback.gui_finalize(0)
          tabid = $('#' + this.mCallback.getId()).prop('tabid')
          if (tabid !== undefined) {
            this.mCallback.gui_inalize(tabid + 1)
          } else {
            this.mCallback.gui_finalize(1)
          }
        }
      }, this),
      buttons: this.getButtonList(),
      close: $.proxy(function (event, ui) {
        unusedVariables(event, ui)
        this.close()
      }, this)
    }
    if (!isModal) {
      args.width = 1200
      args.height = 600
    }
    $('#' + this.mId).dialog(args)
    if (isModal) {
      $('#' + this.mId).css('max-height', String($(window).height() - 150) + 'px')
      $('#' + this.mId).parent().css('top', String(($(window).height() - $('#' + this.mId).parent().height()) / 2) + 'px')
    }
    if (this.mCallback !== null) {
      titlebar = $('#' + this.mId).parent().find('.ui-dialog-titlebar')
      $('<button id=\'refresh_' + this.mId + '\' class=\'ui-button ui-widget ui-state-default ui-corner-all ui-button-icon-only ui-dialog-titlebar-refresh\' role=\'button\' aria-disabled=\'false\' title=\'refresh\'></button>')
        .append('<span class=\'ui-button-icon-primary ui-icon ui-icon-refresh\'/>')
        .append('<span class=\'ui-button-text\'>refresh</span>')
        .appendTo(titlebar)
        .hover(function () { $(this).addClass('ui-state-hover') }, function () { $(this).removeClass('ui-state-hover') })
        .click($.proxy(function () { this.refresh() }, this.mCallback))
      if (!isModal) {
        $('<button id=\'fullscreen_' + this.mId + '\' class=\'ui-button ui-widget ui-state-default ui-corner-all ui-button-icon-only ui-dialog-titlebar-fullscreen\' role=\'button\' aria-disabled=\'false\' title=\'full\'></button>')
          .append('<span class=\'ui-button-icon-primary ui-icon ui-icon-arrow-4-diag\'/>')
          .append('<span class=\'ui-button-text\'>full</span>')
          .appendTo(titlebar)
        $('#fullscreen_' + this.mId).click($.proxy(this.fullscreen, this))
      }
    }
    $('#' + this.mId).keyup($.proxy(this.manageKey, this))
    $('#' + this.mId).css('padding', '0em .5em 2em .5em')
  }

  resizeScreen (width, height, top, left) {
    var idHgt
    var parentHgt
    var diffHgt
    idHgt = $('#' + this.mId).height()
    parentHgt = $('#' + this.mId).parent().height()
    $('#' + this.mId).parent().css({
      'width': width,
      'height': height,
      'left': left,
      'top': top
    })
    diffHgt = $('#' + this.mId).parent().height() - parentHgt
    $('#' + this.mId).height(idHgt + diffHgt)
  }

  fullscreen () {
    var newWidth
    var newHeight
    var newTop
    var newLeft
    var oldSize = $('#' + this.mId).data('oldSize')
    if ((oldSize === undefined) || (oldSize === null)) {
      newWidth = $(document).width()
      newHeight = $(document).height()
      newTop = '0px'
      newLeft = '0px'
      $('#' + this.mId).data('oldSize', [$('#' + this.mId).parent().width(), $('#' + this.mId).parent().height(), $('#' + this.mId).parent().css('top'), $('#' + this.mId).parent().css('left')])
    } else {
      newWidth = oldSize[0]
      newHeight = oldSize[1]
      newTop = oldSize[2]
      newLeft = oldSize[3]
      $('#' + this.mId).data('oldSize', null)
    }
    this.resizeScreen(newWidth, newHeight, newTop, newLeft)
  }

  manageKey (event) {
    var btn
    if ((event.keyCode === 13) && (this.defaultbtn !== '')) {
      btn = $('#' + this.mCallback.getId()).find(this.defaultbtn)
      if (btn.length === 1) {
        btn.click()
        btn.focusout()
        btn.change()
      }
    }
  }

  correctStruct () {
    if ($('#' + this.mId).hasClass('ui-dialog-content')) {
      $('#' + this.mId).dialog('option', 'buttons', this.getButtonList())
    }
  }

  buildFinal () {
    var parent = $('#' + this.mId).parent()
    var iAct
    var btnIcon
    var btn
    var callback = this.mCallback
    $('#' + this.mId + ' .tabContent').each(function () {
      $(this).tabs({
        activate: $.proxy(function (event, ui) {
          var tabid = ui.newTab.index()
          unusedVariables(event)
          this.parent().prop('tabid', tabid)
          if ((callback !== null) && (callback.gui_finalize !== undefined)) {
            callback.gui_finalize(tabid + 1)
          }
        }, $(this))
      })
    })
    $('.datepicker').each(function () {
      $(this).datepicker({
        showOn: 'button',
        buttonImage: 'images/calendar.png',
        buttonImageOnly: true,
        changeMonth: true,
        changeYear: true,
        dateFormat: 'dd/mm/yy'
      }, $.datepicker.regional.fr)
    })
    for (iAct = 0; iAct < this.mButtons.length; iAct++) {
      if (this.mButtons[iAct].getIcon() !== '') {
        btnIcon = this.mButtons[iAct].getIcon()
        if (btnIcon.startsWith('/static/')) {
          btnIcon = Singleton().Transport().getIconUrl(btnIcon)
        }
        btn = parent.find(util.format('div > div.lct-dlgbtnset > button:eq(%s)', iAct))
        btn.find('img').remove()
        btn.prepend(util.format('<img height=\'24px\' src=\'%s\' />', btnIcon))
      }
    }
    if (this.mButtons.length === 0) {
      btn = parent.find('div > div.lct-dlgbtnset > button:eq(0)')
      if ((btn.length === 1) && (parent.find('div > div > button:eq(1)').length === 0)) {
        btnIcon = 'images/close.png'
        btn.find('img').remove()
        btn.prepend(util.format('<img height=\'24px\' src=\'%s\' />', btnIcon))
      }
    }
    this.changeSizeChildreen()
  }

  changeSizeChildreen () {
    var childreen
    var height
    var sumHeight = 0
    var childIdx
    var newHeight
    $('#' + this.mId).data('size', [$('#' + this.mId).parent().width(), $('#' + this.mId).parent().height(), $('#' + this.mId).parent().css('top'), $('#' + this.mId).parent().css('left')])
    childreen = $('#' + this.mId)[0].childNodes
    if (childreen.length > 1) {
      for (childIdx = 0; childIdx < childreen.length; childIdx++) {
        sumHeight = sumHeight + childreen[childIdx].clientHeight
      }
      height = $('#' + this.mId)[0].clientHeight
      newHeight = childreen[childreen.length - 1].clientHeight + height - sumHeight - 50
      childreen[childreen.length - 1].style['min-height'] = newHeight + 'px'
    }
  }

  reloadSize () {
    var newWidth
    var newHeight
    var newTop
    var newLeft
    var currentSize = $('#' + this.mId).data('size')
    if ((currentSize !== undefined) && (currentSize !== null)) {
      newWidth = currentSize[0]
      newHeight = currentSize[1]
      newTop = currentSize[2]
      newLeft = currentSize[3]
      this.resizeScreen(newWidth, newHeight, newTop, newLeft)
    }
  }

  dispose () {
    if (document.getElementById(this.mId) !== null) {
      try {
        $('#' + this.mId).dialog('destroy')
      } catch (err) {
        postLog('dialog.destroy:' + err)
      }
      $('#' + this.mId).remove()
    }
  }
}

export function formatValue (value, formatNum) {
  var options = null
  var subFormat = null
  if ((value !== null) && (typeof value === 'object')) {
    if (value.hasOwnProperty('format')) {
      subFormat = value.format
    }
    if (value.hasOwnProperty('value')) {
      value = value.value
    } else {
      value = null
    }
  }

  if (value === null) {
    value = '---'
    formatNum = ''
  }
  if (typeof formatNum === 'object') {
    if (formatNum.hasOwnProperty(value)) {
      value = formatNum[value]
    }
    formatNum = ''
  }
  if (formatNum === 'B') {
    if (value === true) {
      value = Singleton().getTranslate('Yes')
    } else {
      value = Singleton().getTranslate('No')
    }
  }
  if (formatNum === 'T') {
    value = new Date('1900-01-01 ' + value)
    options = { hour: '2-digit', minute: '2-digit' }
  }
  if (formatNum === 'D') {
    value = new Date(value)
    options = { year: 'numeric', month: 'long', day: 'numeric' }
  }
  if (formatNum === 'H') {
    value = new Date(value)
    options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' }
  }
  if (formatNum.substr(0, 1) === 'N') {
    value = Number(value)
    options = { minimumFractionDigits: Number(formatNum.substr(1)), maximumFractionDigits: Number(formatNum.substr(1)) }
  }
  if (formatNum.substr(0, 1) === 'C') {
    value = Number(value)
    options = { minimumFractionDigits: Number(formatNum.substr(1, 1)), maximumFractionDigits: Number(formatNum.substr(1, 1)), style: 'currency', currency: formatNum.substr(2), currencyDisplay: 'symbol' }
  }
  if (options !== null) {
    value = value.toLocaleString(Singleton().getSelectLang(), options)
  }
  if (subFormat !== null) {
    subFormat = subFormat.replace(/\{([0-9])\}/g, '%s')
    if (subFormat.search('%s') !== -1) {
      value = util.format(subFormat, value)
    } else {
      value = subFormat
    }
  }
  return value
}

export function formatToString (value, formatNum, formatStr) {
  var valIdx
  if (formatNum === null) {
    formatNum = ''
  }
  if (formatStr === null) {
    formatStr = '{0}'
  }
  if (formatStr.indexOf(';') !== -1) {
    formatStr = formatStr.split(';')
    if ((Math.abs(Number(value)) < 0.00001) && (formatStr.length > 2) && (formatStr[2] !== '')) {
      formatStr = formatStr[2]
      value = Number(value)
    } else {
      if ((Number(value) < 0.00001) && (formatStr.length > 1) && (formatStr[1] !== '')) {
        formatStr = formatStr[1]
        value = Math.abs(Number(value))
      } else {
        formatStr = formatStr[0]
      }
    }
  }

  if (Array.isArray(value)) {
    for (valIdx = 0; valIdx < value.length; valIdx++) {
      value[valIdx] = formatValue(value[valIdx], formatNum)
    }
    if (formatStr.indexOf('{1}') === -1) {
      value = [value.join('{[br/]}')]
    }
  } else {
    value = [formatValue(value, formatNum)]
  }
  formatStr = formatStr.replace(/\{([0-9])\}/g, '%s')
  if (formatStr.search('%s') !== -1) {
    return util.format(formatStr, ...value)
  } else {
    return formatStr
  }
}

export class CompBasic {
  constructor (aHtml, aColspan, aRowspan, aStyle) {
    this.html = this.defvalue(aHtml, '')
    this.colspan = this.defvalue(aColspan, 1)
    this.rowspan = this.defvalue(aRowspan, 1)
    this.style = this.defvalue(aStyle, '')
  }

  defvalue (aVal, aDefault) {
    if (aVal === undefined) {
      return aDefault
    }
    return aVal
  }

  getHtml () {
    return this.html
  }
}

export function createTable (compArray) {
  // traitement de la grille de placement des elements
  var line
  var compo
  var html = '<table width=\'100%\'>'
  var rowIdx
  var colIdx
  var colspanIdx
  var rowspanIdx
  for (rowIdx = 0; rowIdx < compArray.length; rowIdx++) {
    if ((compArray[rowIdx] instanceof Array) && (compArray[rowIdx].length > 0)) {
      html += '<tr>'
      line = compArray[rowIdx]
      for (colIdx = 0; colIdx < line.length; colIdx++) {
        if ((line[colIdx] !== undefined) && (line[colIdx] !== null)) {
          compo = line[colIdx]
          html += util.format('<td rowspan=\'%s\' colspan=\'%s\' style=\'%s\'>%s</td>', compo.rowspan, compo.colspan, compo.style, compo.getHtml())
          for (colspanIdx = 0; colspanIdx < compo.colspan; colspanIdx++) {
            line[colIdx + colspanIdx] = null
            for (rowspanIdx = 0; rowspanIdx < compo.rowspan; rowspanIdx++) {
              if (!(compArray[rowIdx + rowspanIdx] instanceof Array)) {
                compArray[rowIdx + rowspanIdx] = []
              }
              compArray[rowIdx + rowspanIdx][colIdx + colspanIdx] = null
            }
          }
        } else if (line[colIdx] === undefined) {
          html += '<td/>'
        }
      }
      html += '</tr>'
    }
  }
  html += '</table>'
  return html
}

export function createTab (tabs, tabcontents) {
  var tabId = createGuid()
  var html = '<div class=\'tabContent\'>'
  var tabIdx
  var tabcontentvalue
  html += '<ul>'
  for (tabIdx = 0; tabIdx < tabs.length; tabIdx++) {
    html += util.format('<li><a href=\'#tab_%s_%s\'>%s</a></li>', tabId, tabIdx, tabs[tabIdx])
  }
  html += '</ul>'
  for (tabIdx = 0; tabIdx < tabcontents.length; tabIdx++) {
    tabcontentvalue = tabcontents[tabIdx]
    if (tabcontentvalue instanceof Array) {
      tabcontentvalue = createTable(tabcontentvalue)
    }
    html += util.format('<div id=\'tab_%s_%s\'>%s</div>', tabId, tabIdx, tabcontentvalue)
  }
  html += '</div>'
  return html
}
