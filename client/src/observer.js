'use strict'
import { unusedVariables, HashMap, createGuid } from './utils.js'
import { Singleton } from './singleton.js'
import { FORM_MODAL, FORM_REFRESH } from './action.js'

export class ObserverAbstract {
  constructor () {
    this.mExtension = ''
    this.mAction = ''
    this.mTitle = ''
    this.mContext = new HashMap()
    this.mJSON = null
    this.mCloseAction = null
    this.mRefresh = null
    this.mGUIType = FORM_MODAL
    this.mParent = null
    this.mID = createGuid()
    this.mGUI = null
    this.closed = false
  }

  getId () {
    return this.mID
  }

  getParent () {
    return this.mParent
  }

  setParent (aParent) {
    this.mParent = aParent
  }

  init () {
    ObserverAbstract.ObserverName = ''
  }

  getObserverName () {
    return ObserverAbstract.ObserverName
  }

  getSourceAction () {
    return this.mAction
  }

  getSourceMethod () {
    return this.mMethod
  }

  getSourceExtension () {
    return this.mExtension
  }

  getContext () {
    return this.mContext
  }

  getContent () {
    return this.mJSON
  }

  getType () {
    return this.mType
  }

  getContentText () {
    return JSON.stringify(this.mJSON)
  }

  getTitle () {
    return this.mTitle
  }

  setSource (aExtension, aAction, aMethod) {
    this.mID = createGuid()
    this.mExtension = aExtension
    this.mAction = aAction
    this.mMethod = aMethod
  }

  setCaption (aTitle) {
    this.mTitle = aTitle
  }

  fillContext () {
    var params
    var index
    var contexts = this.mJSON.context
    this.mContext = new HashMap()
    if (contexts) {
      params = Object.keys(contexts)
      for (index = 0; index < params.length; index++) {
        this.mContext.put(params[index], contexts[params[index]])
      }
    }
  }

  setContent (aJSON) {
    this.mJSON = aJSON
    if (this.mJSON !== null) {
      this.fillContext()
      if (this.mJSON.close) {
        if (this.mCloseAction === null) {
          this.mCloseAction = Singleton().CreateAction()
          this.mCloseAction.initialize(this, Singleton().Factory(), this.mJSON.close)
          this.mCloseAction.setCheckNull(false)
          this.mCloseAction.setClose(true)
          this.mCloseAction.setUsedContext(true)
        }
      }
      this.mRefresh = Singleton().CreateAction()
      this.mRefresh.initializeEx(this, Singleton().Factory(), this.getTitle(), this.getSourceExtension(), this.getSourceAction(), this.getSourceMethod())
      this.mRefresh.setFormType(FORM_REFRESH)
      this.mRefresh.setClose(false)
      this.mRefresh.setUsedContext(true)
    }
  }

  show (aTitle, aGUIType) {
    if (this.mTitle === '') {
      this.mTitle = aTitle
    }
    this.mGUIType = aGUIType
  }

  setActive (aIsActive) {
    unusedVariables(aIsActive)
  }

  async close () {
    if (!this.closed) {
      this.closed = true
      this.closeEx()
      if (this.mCloseAction !== null) {
        await this.mCloseAction.actionPerformed()
      }
      this.mCloseAction = null
      var parent = this.getParent()
      if (parent !== null) {
        await parent.refresh()
      }
    }
  }

  async refresh () {
    if (this.mRefresh !== null) {
      await this.mRefresh.actionPerformed()
    }
  }

  closeEx () {
    return undefined
  }

  getParameters (aCheckNull) {
    unusedVariables(aCheckNull)
    return new HashMap()
  }

  getGUI () {
    return this.mGUI
  }
}

export class ObserverGUI extends ObserverAbstract {
  constructor () {
    super()
    this.mActions = null
  }

  setContent (aJSON) {
    super.setContent(aJSON)
    this.mActions = this.mJSON.actions
  }

  buildButtons () {
    var btns = []
    var index
    var newact
    if (this.mActions) {
      for (index = 0; index < this.mActions.length; index++) {
        newact = Singleton().CreateAction()
        newact.initialize(this, Singleton().Factory(), this.mActions[index])
        btns[btns.length] = newact
      }
    }
    return btns
  }

  closeEx () {
    if (this.mGUI !== null) {
      this.mGUI.dispose()
    }
  }

  setActive (aIsActive) {
    if (this.mGUI !== null) {
      this.mGUI.setActive(aIsActive)
    }
  }
}
