'use strict'
import { unusedVariables, HashMap, postLog, LucteriosException, IMPORTANT, GRAVE } from './utils.js'
const Blob = require('node-blob')

export class ObserverFactoryAbstract {
  constructor () {
    this.mParameters = ''
    this.mTransport = null
    this.mObserverList = new HashMap()
  }

  setHttpTransport (aHttpTransport) {
    this.mTransport = aHttpTransport
  }

  clearObserverList () {
    this.mObserverList = new HashMap()
  }

  AddObserver (aObsName, aObserverClass) {
    this.mObserverList.put(aObsName, aObserverClass)
  }

  factoryObserver (aObserverName) {
    var ObserverClass = this.mObserverList.get(aObserverName)
    return new ObserverClass()
  }

  transfertFromServer (aExtension, aAction, aParam, aMethod) {
    unusedVariables(aExtension, aAction, aParam, aMethod)
    return null
  }

  async callAction (aExtension, aAction, aParam, aMethod) {
    unusedVariables(aExtension, aAction, aParam, aMethod)
    return null
  }

  async setAuthentification (aLogin, aPassWord) {
    var res = false
    var param = new HashMap()
    var aut
    var xmlAuth
    var session
    if ((aLogin === null)) {
      param.put('ses', aPassWord)
      param.put('info', '1')
    } else {
      param.put('username', aLogin)
      param.put('password', aPassWord)
      this.mTransport.setLastLogin(aLogin)
    }
    aut = await this.callAction('CORE', 'authentification', param, null, 'POST')
    if (aut.getObserverName() === 'core.auth') {
      xmlAuth = aut.getContent()
      if (xmlAuth.context && xmlAuth.context.ses) {
        session = xmlAuth.context.ses
        res = (session !== '')
        if (res) {
          this.mTransport.setSession(session)
        }
      }
    }
    aut.show('')
    return res
  }
}

export class ObserverFactoryRestImpl extends ObserverFactoryAbstract {
  async callAction (aExtension, aAction, aParam, aObserver, aMethod) {
    var resObs = null
    var jsonRep = await this.transfertFromServer(aExtension, aAction, aParam, aMethod)
    var observerName
    var sourceExtension
    var sourceAction
    if (jsonRep && jsonRep.meta) {
      observerName = jsonRep.meta.observer
      if (this.mObserverList.hasOwnProperty(observerName)) {
        sourceExtension = jsonRep.meta.extension
        sourceAction = jsonRep.meta.action
        if (aObserver === null) {
          resObs = this.factoryObserver(observerName)
          resObs.setSource(sourceExtension, sourceAction, aMethod)
        } else {
          resObs = aObserver
          if ((resObs.getObserverName() !== observerName) || (sourceAction === '') || (sourceExtension === '')) {
            if ((observerName === 'core.auth') || (observerName === 'core.exception')) {
              resObs = this.factoryObserver(observerName)
              resObs.setSource(sourceExtension, sourceAction, aMethod)
            } else {
              throw new LucteriosException(GRAVE, 'Erreur de parsing (refresh)' + aObserver.getObserverName() + ' -> ' + observerName,
                this.mParameters, JSON.stringify(jsonRep))
            }
          }
        }
        if (jsonRep.meta.title) {
          resObs.setCaption(jsonRep.meta.title)
        } else {
          resObs.setCaption('')
        }
        resObs.setContent(jsonRep)
      } else {
        throw new LucteriosException(IMPORTANT, 'Observeur \'' + observerName + '\' inconnu.', this.mParameters, JSON.stringify(jsonRep))
      }
    } else {
      throw new LucteriosException(GRAVE, 'Erreur inconnu', this.mParameters, jsonRep.toString())
    }
    return resObs
  }
  transfertFromServer (aExtension, aAction, aParam, aMethod) {
    var val
    var self = this
    var webFile = aExtension + '/' + aAction
    this.mParameters = webFile + '?'
    aParam.keys().forEach(function (key) {
      val = aParam.get(key)
      if (typeof val === 'string') {
        if (self.mParameters !== '') {
          self.mParameters += '&'
        }
        self.mParameters += key + '=' + val
      } else {
        if (val instanceof Blob) {
          if (self.mParameters !== '') {
            self.mParameters += '&'
          }
          self.mParameters += key + '=' + val.name
        }
      }
    })
    postLog('Ask ' + self.mParameters)
    return this.mTransport.transfertFileFromServerString(webFile, aParam, aMethod)
  }
}
