'use strict'
import { HashMap, createGuid } from './utils.js'
const $ = require('jquery')

export var FORM_NOMODAL = 0
export var FORM_MODAL = 1
export var FORM_REFRESH = 2

export var SELECT_NONE = 1
export var SELECT_SINGLE = 0
export var SELECT_MULTI = 2

export var MNEMONIC_CHAR = '_'

export class ActionAbstract {
  constructor () {
    this.mOwner = null
    this.mFactory = null
    this.mExtension = ''
    this.mAction = ''
    this.mTitle = ''
    this.mID = ''
    this.mFormType = FORM_NOMODAL
    this.mClose = true
    this.mSelect = SELECT_NONE
    this.mMethod = 'GET'
    this.mIcon = ''
    this.mSizeIcon = ''
    this.mKeyStroke = ''
    this.mExtraParam = null
    this.mCheckNull = true
    this.mEnabled = true
    this.mUsedContext = false
  }

  setEnabled (aEnabled) {
    this.mEnabled = aEnabled
  }

  isEnabled () {
    return this.mEnabled
  }

  initialize (aOwner, aFactory, aJSON) {
    var xmlparams, index
    this.initializeEx(aOwner, aFactory, aJSON.text, aJSON.extension, aJSON.action, aJSON.method)
    if (aJSON.id !== null) {
      this.mID = aJSON.id
    }
    this.mFormType = aJSON.modal ? parseInt(aJSON.modal, 10) : FORM_NOMODAL
    this.mClose = ((aJSON.close ? parseInt(aJSON.close, 10) : 1) !== 0)
    this.mSelect = aJSON.unique ? parseInt(aJSON.unique, 10) : SELECT_NONE
    this.mIcon = aJSON.icon || ''
    this.mSizeIcon = parseInt(aJSON.sizeicon, 10) || 0
    this.mKeyStroke = aJSON.shortcut
    if (aJSON.params) {
      xmlparams = Object.keys(aJSON.params)
      for (index = 0; index < xmlparams.length; index++) {
        this.mExtraParam.put(xmlparams[index], aJSON.params[xmlparams[index]])
      }
    }
  }

  initializeEx (aOwner, aFactory, aTitle, aExtension, aAction, aMethod) {
    this.mOwner = aOwner
    this.mFactory = aFactory
    this.mTitle = aTitle || ''
    this.mExtraParam = new HashMap()
    this.mTitle = this.mTitle.replace(MNEMONIC_CHAR, '')
    this.mExtension = aExtension || ''
    this.mMethod = aMethod || 'GET'
    this.mAction = aAction || ''
    this.mID = createGuid()
  }

  getOwner () {
    return this.mOwner
  }

  getID () {
    return this.mID
  }

  getTitle () {
    return this.mTitle
  }

  getExtension () {
    return this.mExtension
  }

  getAction () {
    return this.mAction
  }

  getIcon () {
    return this.mIcon
  }

  getFormType () {
    return this.mFormType
  }

  getClose () {
    return this.mClose
  }

  getSelect () {
    return this.mSelect
  }

  getCheckNull () {
    return this.mCheckNull
  }

  getUsedContext () {
    return this.mUsedContext
  }

  setUsedContext (aUsedContext) {
    this.mUsedContext = aUsedContext
  }

  setCheckNull (aCheckNull) {
    this.mCheckNull = aCheckNull
  }

  setClose (aClose) {
    this.mClose = aClose
  }

  setFormType (aFormType) {
    this.mFormType = aFormType
  }

  getParameters () {
    var param
    if (this.mOwner !== null) {
      if (this.mUsedContext) {
        param = this.mOwner.getContext()
      } else {
        param = this.mOwner.getParameters(this.mCheckNull)
      }
    } else {
      param = new HashMap()
    }
    if ((param !== null) && (this.mExtraParam !== null) && (this.mExtraParam.size() > 0)) {
      param.putAll(this.mExtraParam)
    }
    return param
  }

  mustPerforme () {
    if (!this.mEnabled) {
      return false
    }
    if ((this.mExtension === '') || (this.mAction === '')) {
      if ((this.mOwner !== null) && (this.mClose)) {
        this.mOwner.close(true)
      }
      return false
    }
    return true
  }

  async actionPerformed () {
    if (this.mustPerforme()) {
      var param = this.getParameters()
      if (param !== null) {
        if ((this.mOwner !== null) && (this.mClose)) {
          this.mOwner.close(false)
        }
        if (this.mOwner !== null) {
          this.mOwner.setActive(false)
        }
        try {
          await this.runAction(param)
        } finally {
          if ((this.mOwner !== null) && (this.mFormType !== FORM_REFRESH)) {
            this.mOwner.setActive(true)
          }
        }
      }
    }
  }

  getButton () {
    var result = {}
    result.text = this.getTitle()
    result.click = $.proxy(this.actionPerformed, this)
    return result
  }
}

export class ActionImpl extends ActionAbstract {
  async runAction (aParam) {
    var oldObservrer = null
    var currentObs = null
    if (this.mFormType === FORM_REFRESH) {
      oldObservrer = this.getOwner()
    }
    currentObs = await this.mFactory.callAction(this.mExtension, this.mAction, aParam, oldObservrer, this.mMethod)

    if (!this.mUsedContext && (this.mOwner !== null)) {
      if ((this.mClose) || (this.mFormType === FORM_REFRESH)) {
        currentObs.setParent(this.mOwner.getParent())
      } else {
        currentObs.setParent(this.mOwner)
      }
    }
    currentObs.show(this.mTitle, this.mFormType)
  }
}

export class ActionInt extends ActionAbstract {
  constructor () {
    super()
    this.callback = null
  }

  mustPerforme () {
    return true
  }

  async runAction (aParam) {
    if (this.callback !== null) {
      await this.callback(aParam)
    }
  }
}
