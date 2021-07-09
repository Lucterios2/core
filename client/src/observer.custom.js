'use strict'
import { HashMap, LucteriosException, GRAVE } from './utils.js'
import { FORM_MODAL } from './action.js'
import { GUIManage, createTable, createTab } from './gui.utils.js'
import { ObserverGUI } from './observer.js'
import { showMessageDialog } from './observer.dialogbox.js'
import { CompCaptcha, CompImage, CompLabelForm, CompEdit, CompFloat, CompMemo, CompXML, CompCheck, CompLink, CompSelect, CompCheckList, CompButton, CompDate, CompTime, CompDateTime, CompPassword, CompUpload, CompDownload } from './observer.custom.comp.js'
import { CompGrid } from './observer.custom.grid.js'
const $ = require('jquery')
const util = require('util')

export class ObserverCustom extends ObserverGUI {
  constructor () {
    super()
    this.mCompList = new HashMap()
    this.mDefaultBtn = ''
  }

  get (key) {
    return this.mCompList[key]
  }

  getObserverName () {
    return 'core.custom'
  }

  savefocusin (event) {
    $('#' + this.getId()).prop('fieldname', event.target.getAttribute('name'))
  }

  show (aTitle, aGUIType) {
    super.show(aTitle, aGUIType)
    this.setActive(true)

    var compIdx, fieldname, guiVal, tabid, oldSize
    this.mGUI = new GUIManage(this.getId(), this.mTitle, this)
    this.mGUI.addcontent(this.getHtmlFromComponent(), this.buildButtons())
    this.mGUI.defaultbtn = this.mDefaultBtn
    this.mGUI.showGUI(aGUIType === FORM_MODAL)
    for (compIdx = 0; compIdx < this.mCompList.size(); compIdx++) {
      guiVal = this.mCompList.val(compIdx)
      if (guiVal !== null) {
        guiVal.addAction()
        guiVal.getGUIComp().focusin($.proxy(this.savefocusin, this))
      }
    }
    this.guiFinalize(0)
    tabid = $('#' + this.getId()).prop('tabid')
    if (tabid !== undefined) {
      $('#' + this.getId()).find(util.format('ul > li:eq(%s) > a', tabid)).click()
    } else {
      this.guiFinalize(1)
    }
    fieldname = $('#' + this.getId()).prop('fieldname')
    if (fieldname !== undefined) {
      $('#' + this.getId()).find(util.format('[name=\'%s\']:eq(0)', fieldname)).focus()
    }
    oldSize = $('#' + this.getId()).data('oldSize')
    if ((oldSize !== undefined) && (oldSize !== null)) {
      $('#' + this.getId()).data('oldSize', null)
      this.mGUI.fullscreen()
    } else {
      this.mGUI.reloadSize()
    }
  }

  checkCompoundValid () {
    var cmp
    var compIdx
    try {
      for (compIdx = 0; compIdx < this.mCompList.size(); compIdx++) {
        cmp = this.mCompList.val(compIdx)
        cmp.checkValid()
      }
    } catch (lctept) {
      if (cmp !== null) {
        cmp.getGUIComp().focus()
      }
      if (lctept.message !== '') {
        showMessageDialog(lctept.message, this.getTitle())
      }
      return false
    }
    return true
  }

  getParameters (aCheckNull) {
    if (!aCheckNull || this.checkCompoundValid()) {
      var params = new HashMap()
      var compIdx
      params.putAll(this.mContext)
      for (compIdx = 0; compIdx < this.mCompList.size(); compIdx++) {
        this.mCompList.val(compIdx).fillValue(params)
      }
      return params
    }
    return null
  }

  getHtmlFromComponent () {
    var compArray = []
    var hasTabs = false
    var tabs = []
    var tabContent = []
    var actualTab = -1
    var compType
    var components
    var iComp
    var component
    var comp
    var html

    this.mCompList = new HashMap()
    components = this.mJSON.comp
    if (components) {
      for (iComp = 0; iComp < components.length; iComp++) {
        component = components[iComp]
        component.value = this.mJSON.data[component.name]
        compType = component.component
        if (compType !== undefined) {
          switch (compType) {
            case 'IMAGE':
              comp = new CompImage(this)
              break
            case 'LABELFORM':
              comp = new CompLabelForm(this)
              break
            case 'EDIT':
              comp = new CompEdit(this)
              break
            case 'FLOAT':
              comp = new CompFloat(this)
              break
            case 'MEMO':
              comp = new CompMemo(this)
              break
            case 'XML':
              comp = new CompXML(this)
              break
            case 'CHECK':
              comp = new CompCheck(this)
              break
            case 'GRID':
              comp = new CompGrid(this)
              break
            case 'LINK':
              comp = new CompLink(this)
              break
            case 'SELECT':
              comp = new CompSelect(this)
              break
            case 'CHECKLIST':
              comp = new CompCheckList(this)
              break
            case 'BUTTON':
              comp = new CompButton(this)
              break
            case 'DATE':
              comp = new CompDate(this)
              break
            case 'TIME':
              comp = new CompTime(this)
              break
            case 'DATETIME':
              comp = new CompDateTime(this)
              break
            case 'PASSWD':
              comp = new CompPassword(this)
              break
            case 'UPLOAD':
              comp = new CompUpload(this)
              break
            case 'DOWNLOAD':
              comp = new CompDownload(this)
              break
            case 'CAPTCHA':
              comp = new CompCaptcha(this)
              break
            case 'TAB':
              hasTabs = true
              actualTab++
              tabs[actualTab] = component.value
              tabContent[actualTab] = []
              break
            default:
              throw new LucteriosException(GRAVE, 'Unknown composant:' + compType)
          }
          if (compType !== 'TAB') {
            comp.initial(component)
            if (hasTabs) {
              if (tabContent[actualTab][comp.y] === undefined) {
                tabContent[actualTab][comp.y] = []
              }
              tabContent[actualTab][comp.y][comp.x] = comp
            } else {
              if (compArray[comp.y] === undefined) {
                compArray[comp.y] = []
              }
              compArray[comp.y][comp.x] = comp
            }
            this.mCompList.put(comp.name, comp)
          }
        }
      }
    }

    html = createTable(compArray)
    if (hasTabs) {
      html += createTab(tabs, tabContent)
    }
    return html
  }

  guiFinalize (tabid) {
    var cmp
    var compIdx
    for (compIdx = 0; compIdx < this.mCompList.size(); compIdx++) {
      cmp = this.mCompList.val(compIdx)
      if (cmp.tab === tabid) {
        cmp.guiFinalize()
      }
    }
  }
}
