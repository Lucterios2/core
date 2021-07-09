'use strict'
import { HashMap, unusedVariables } from './utils.js'
import { ObserverAbstract } from './observer.js'
import { Singleton } from './singleton.js'

export class ObserverAcknowledge extends ObserverAbstract {
  constructor () {
    super()
    this.mRedirectAction = null
  }

  getRedirectAction () {
    return this.mRedirectAction
  }

  setContent (aJSON) {
    super.setContent(aJSON)
    if (this.mJSON.action) {
      this.mRedirectAction = Singleton().CreateAction()
      this.mRedirectAction.initialize(this, Singleton().Factory(), this.mJSON.action)
      this.mRedirectAction.setClose(true)
    } else {
      this.mRedirectAction = null
    }
  }

  getObserverName () {
    return 'core.acknowledge'
  }

  getParameters (aCheckNull) {
    unusedVariables(aCheckNull)
    var requete = new HashMap()
    requete.putAll(this.mContext)
    return requete
  }

  show (aTitle, aGUIType) {
    super.show(aTitle, aGUIType)
    this.setActive(true)
    if (this.mRedirectAction !== null) {
      this.mRedirectAction.actionPerformed()
    }
    this.close(this.mRedirectAction === null)
  }
}
