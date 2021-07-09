'use strict'
import { HashMap, unusedVariables, createGuid, GWithExtraMenu, convertLuctoriosFormatToHtml } from './utils.js'
import { Singleton } from './singleton.js'
import { createTab } from './gui.utils.js'
import { ObserverAbstract } from './observer.js'
import { ObserverCustom } from './observer.custom.js'
const $ = require('jquery')
const util = require('util')

export function resizeContentTabs () {
  var tabsPanelHeight
  if ($(window).width() > 1000) {
    $('#asideMenu').css('display', 'block')
    tabsPanelHeight = $(window).height() - 130
  } else if ($(window).width() > 623) {
    tabsPanelHeight = $(window).height() - 180
  } else {
    tabsPanelHeight = $(window).height() - 130
  }
  $('.ui-tabs-panel').css('max-height', tabsPanelHeight + 'px')
  if ($(window).height() < 570) {
    $('.ui-accordion-content').css('height', (tabsPanelHeight + 10) + 'px')
  }
}

export function infoOpenClose () {
  var valDisplay = $('#asideMenu').css('display')
  if (valDisplay === 'none') {
    $('#asideMenu').css('display', 'block')
    $('#support').css('display', 'block')
    $('#menuContainer').removeClass('menupos')
    $('#asideMenu').accordion('option', 'active', 0)
  } else {
    $('#asideMenu').css('display', 'none')
    $('#support').css('display', 'none')
    $('#menuContainer').addClass('menupos')
  }
}

export class Menu {
  constructor (menu, level, owner) {
    this.rootHtml = ''
    this.obs = null
    this.level = level
    this.submenu = []

    this.id = menu.id.replace(/[_.()'`/]/g, '')
    if (this.id !== 'coremenu') {
      this.id += '_' + createGuid()
    }
    this.icon = menu.icon || ''
    this.extension = menu.extension || ''
    this.action = menu.action || ''
    this.modal = parseInt(menu.modal, 10) || 0
    this.help = menu.help || ''
    this.txt = menu.text || ''

    if (this.action !== '') {
      this.act = Singleton().CreateAction()
      this.act.initialize(owner, Singleton().Factory(), menu)
      this.act.setClose(false)
    } else {
      this.act = null
    }
    if (menu.menus !== undefined) {
      var issMen
      var menuItem
      for (issMen = 0; issMen < menu.menus.length; issMen++) {
        menuItem = new Menu(menu.menus[issMen], ++level, owner)
        if ((((menuItem.icon !== '') || GWithExtraMenu) && (menuItem.action !== null)) || (menuItem.submenu.length > 0)) {
          this.submenu.push(menuItem)
        }
      }
    }
  }

  getActFrame (itemType, style, isRootLevel) {
    var html = ''
    var defaultStyle
    var submenuIdx
    if ((this.icon !== '') || GWithExtraMenu) {
      html = util.format('<%s id=\'%s\' %s>', itemType, this.id, style)
      if (isRootLevel === false) {
        if (this.icon !== '') {
          html += util.format('<img src=\'%s\' />', Singleton().Transport().getIconUrl(this.icon))
        }
        html += util.format('<label><b>%s</b></label>', this.txt)
      }
      if (this.help !== null && this.help !== '') {
        if (itemType === 'div') {
          html += util.format('<span class=\'fa fa-question-circle\' onclick=\'toggleHelp("%s")\'></span>', this.id)
          defaultStyle = 'display:none;'
        } else {
          defaultStyle = 'display:line;'
        }
        html += util.format('<div class=\'helper\' style=\'%s\' >', defaultStyle)
        html += util.format('<label>%s</label>', convertLuctoriosFormatToHtml(this.help))
        html += '</div>'
      }
      html += util.format('</%s>', itemType)
    }
    for (submenuIdx = 0; submenuIdx < this.submenu.length; submenuIdx++) {
      html += this.submenu[submenuIdx].getHtml()
    }
    return html
  }

  getHtml () {
    this.rootHtml = ''
    var html = ''
    // menu principal type dropdown sans action
    if (this.act === null) {
      // tabs de menu
      if (this.level === 0) {
        if (this.icon !== '') {
          this.rootHtml += util.format('<img src=\'%s\' />', Singleton().Transport().getIconUrl(this.icon))
        }
        this.rootHtml += util.format('<span>%s</span>', this.txt)
        html += this.getActFrame('div', 'class=\'rootFrame\'', true)
      } else {
        html += this.getActFrame('div', 'class=\'menuFrame\'', false)
      }
    } else {
      html += this.getActFrame('button', '', false)
    }
    return html
  }

  addAction () {
    var actFunction
    var comp
    var submenuIdx
    if (this.obs !== null) {
      this.obs.show('')
      this.obs.refresh()
      actFunction = function () {
        this.refresh()
      }
      comp = $(util.format('#title_%s', this.obs.getId()))
      comp.click($.proxy(actFunction, this.obs))
    } else if (this.act !== null) {
      actFunction = function () {
        this.act.actionPerformed()
      }
      comp = $(util.format('#%s', this.id))
      comp.click($.proxy(actFunction, this))
    }
    for (submenuIdx = 0; submenuIdx < this.submenu.length; submenuIdx++) {
      this.submenu[submenuIdx].addAction()
    }
  }
}

export class ObserverMenu extends ObserverAbstract {
  constructor () {
    super()
    this.menu_json = null
    this.menu_list = null
    this.aside_menu = null
  }

  setContent (aJSON) {
    super.setContent(aJSON)
    this.menu_json = aJSON.menus
    this.mRefresh = null
  }

  getObserverName () {
    return 'Core.Menu'
  }

  getParameters (aCheckNull) {
    unusedVariables(aCheckNull)
    var requete = new HashMap()
    requete.putAll(this.mContext)
    return requete
  }

  setActive (aIsActive) {
    var submenuIdx
    var currentMenu
    var bts
    if (this.aside_menu) {
      for (submenuIdx = 0; submenuIdx < this.aside_menu.submenu.length; submenuIdx++) {
        currentMenu = this.aside_menu.submenu[submenuIdx]
        currentMenu.obs.setActive(aIsActive)
        $(util.format('#title_%s', currentMenu.txt)).prop('disabled', !aIsActive)
      }
    }
    bts = $('#menuContainer > div > div > button')
    bts.prop('disabled', !aIsActive)
  }

  closeEx () {
    $('#mainMenu').remove()
  }

  show (aTitle, aGUIType) {
    super.show(aTitle, aGUIType)
    this.setActive(true)

    this.aside_menu = null
    var roothtml = []
    var html = []
    var iMen
    var menuItem
    var menuIdx
    this.menu_list = []
    for (iMen = 0; iMen < this.menu_json.length; iMen++) {
      menuItem = new Menu(this.menu_json[iMen], 0, this)
      if ((menuItem.id === 'coremenu') && (menuItem.submenu.length > 0)) {
        this.aside_menu = menuItem
      } else if (menuItem.submenu.length > 0) {
        html.push(menuItem.getHtml())
        roothtml.push(menuItem.rootHtml)
      }
      if (menuItem.submenu.length > 0) {
        this.menu_list.push(menuItem)
      }
    }
    $('#mainMenu').remove()
    $('#lucteriosClient').append('<div id=\'mainMenu\' style=\'display:none;\'/>')
    this.buildAsideMenu()
    html = '<div id=\'menuContainer\'>' + createTab(roothtml, html) + '</div>'
    $('#mainMenu').append(html)
    $('.tabContent').each(function () {
      $(this).tabs()
    })
    for (menuIdx = 0; menuIdx < this.menu_list.length; menuIdx++) {
      this.menu_list[menuIdx].addAction()
    }
    window.removeEventListener('resize', resizeContentTabs)
    resizeContentTabs()
    window.addEventListener('resize', resizeContentTabs)
    $('#mainMenu').css('display', 'block')
    if ((Singleton().mDesc !== null) && (Singleton().mDesc.mSupportHTML !== '')) {
      $('#mainMenu').append('<div id=\'support\'>' + convertLuctoriosFormatToHtml(Singleton().mDesc.mSupportHTML) + '</div>')
    }
    if ((Singleton().mDesc !== null) && (!Singleton().mDesc.isCordovaVersionOk())) {
      $('#mainMenu').append('<div id=\'versionclient\'>' + Singleton().getTranslate('Client obselete') + '</div>')
    }
    if (this.aside_menu === null) {
      $('#menuContainer').css('left', '0px')
      $('#support').css('display', 'none')
      $('#showmenu').css('display', 'none')
    }
    if (roothtml.length === 1) {
      $('ul[role=\'tablist\']').css('display', 'none')
    }
  }

  buildAsideMenu () {
    var html = ''
    var submenuIdx
    var currentMenu
    var menuContent
    var lastMenu
    var size
    if (this.aside_menu !== null) {
      html = '<div id=\'asideMenu\' class=\'asideprop\'>'
      for (submenuIdx = 0; submenuIdx < this.aside_menu.submenu.length; submenuIdx++) {
        currentMenu = this.aside_menu.submenu[submenuIdx]
        currentMenu.obs = new ObserverCustom()
        currentMenu.obs.setSource(currentMenu.extension, currentMenu.action)
        currentMenu.obs.setContent({
          'context': {},
          'comp': {},
          'meta': {},
          'data': {}
        })
        currentMenu.obs.mID = util.format('aside_%s', submenuIdx + 1)
        html += util.format('<h3 id=\'title_%s\'>%s</h3>', currentMenu.obs.getId(), currentMenu.txt)
        html += util.format('<div id=\'%s\'></div>', currentMenu.obs.getId())
      }
      html += '</div>'
      $('#mainMenu').append(html)
      $('#asideMenu').accordion({
        collapsible: false,
        activate: function (event, ui) {
          unusedVariables(event, ui)
          var opened = $(this).find('.ui-state-active').length
          if (opened === 0) {
            infoOpenClose()
          }
        }
      })
      size = 481 - this.aside_menu.submenu.length * 26
      for (submenuIdx = 0; submenuIdx < this.aside_menu.submenu.length; submenuIdx++) {
        menuContent = $(util.format('#aside_%s', submenuIdx + 1))[0]
        menuContent.style.height = size + 'px'
        menuContent.style.display = null
      }
      lastMenu = this.aside_menu.submenu[this.aside_menu.submenu.length - 1]
      $(util.format('#title_%s', lastMenu.obs.getId())).click()
    }
    return html
  }
}

export class EmptyObserverMenu extends ObserverMenu {
  getObserverName () {
    return 'Core.Menu'
  }

  show (aTitle, aGUIType) {
    unusedVariables(aTitle, aGUIType)
    $('#mainMenu').remove()
  }
}

export function refreshCurrentAcideMenu () {
  var first = $('#asideMenu h3[aria-expanded=\'true\']:eq(0)')
  var acideMenuId
  var title
  if (first.length) {
    acideMenuId = first.prop('id')
    if (acideMenuId.substring(0, 6) !== 'title_') {
      acideMenuId = 'title_' + acideMenuId
    }
    title = $('#' + acideMenuId)
    title.click()
  }
}

export function toggleHelp (helpId) {
  var helper = $('#' + helpId + ' div.helper:eq(0)')
  if (helper.css('display') === 'none') {
    helper.css('display', 'block')
  } else {
    helper.css('display', 'none')
  }
}
