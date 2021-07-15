'use strict'
import { unusedVariables, getServerUrl, postLog, LucteriosException, CRITIC, GRAVE } from './utils.js'
import { Singleton } from './singleton.js'
import axios from 'axios'
import Cookies from 'js-cookie'
const util = require('util')
const FormData = require('form-data')

export class HttpTransportAbstract {
  constructor () {
    this.mLastLogin = ''
    this.mWaitingOn = function () {}
    this.mWaitingOff = function () {}
  }

  setLastLogin (aLastLogin) {
    this.mLastLogin = aLastLogin
  }

  getLastLogin () {
    return this.mLastLogin
  }

  getServerUrl () {
    return getServerUrl()
  }

  getSession () {
    var session = this.getSessionEx()
    this.setSession(session)
    return session
  }

  getSessionEx () {
    var session = Cookies.get('lucterios_session')
    if (session === undefined) {
      session = ''
    }
    return session
  }

  setSession (session) {
    if (session === '') {
      Cookies.remove('lucterios_session')
      Cookies.remove('sessionid')
    } else {
      Cookies.set('lucterios_session', session)
    }
  }

  transfertFileFromServerString (aWebFile, aParams, aMethod) {
    unusedVariables(aWebFile, aParams, aMethod)
    return ''
  }

  getIconUrl (icon) {
    if (/^data:image/.test(icon)) {
      return icon
    }
    var iconurl = getServerUrl()
    if (icon[0] === '/') {
      iconurl += icon.substring(1)
    } else {
      iconurl += icon
    }
    return iconurl
  }

  close () {
    return this.setSession('')
  }

  getFileContent (aUrl) {
    unusedVariables(aUrl)
  }

  waitingOn () {
    this.mWaitingOn()
  }

  waitingOff () {
    this.mWaitingOff()
  }
}

export class HttpTransportImpl extends HttpTransportAbstract {
  async transfertFileFromServerString (aWebFile, aParams, aMethod) {
    var reponsetext = ''
    var fullurl = this.getServerUrl() + aWebFile
    var formData = new FormData()
    if (aMethod === undefined) {
      aMethod = 'GET'
    }
    if (aParams !== null) {
      if ((aMethod === 'GET') || (aMethod === 'DELETE')) {
        var parts = []
        aParams.keys().forEach(function (key) {
          parts.push(util.format('%s=%s', encodeURIComponent(key), encodeURIComponent(aParams[key])))
        })
        if (parts.length > 0) {
          fullurl += '?' + parts.join('&')
        }
      } else {
        aParams.keys().forEach(function (key) {
          formData.append(key, aParams.get(key))
        })
      }
    }
    var success = function (response) {
      reponsetext = response.data
    }
    var failure = function (error) {
      reponsetext = JSON.stringify(error)
      if (error.response !== undefined) {
        postLog('HTTP ERROR:' + error.response.status + '/' + reponsetext)
        if (error.response.status === 404) {
          throw new LucteriosException(GRAVE, Singleton().getTranslate('Command unknown!'), aWebFile, reponsetext)
        } else {
          throw new LucteriosException(CRITIC, 'Http error ' + error.response.status, aWebFile, reponsetext)
        }
      } else {
        throw new LucteriosException(CRITIC, 'Internal error !', aWebFile, reponsetext)
      }
    }
    this.waitingOn()
    try {
      if (aMethod === 'GET') {
        await axios.get(fullurl).then(success).catch(failure)
      } else if (aMethod === 'POST') {
        await axios.post(fullurl, formData).then(success).catch(failure)
      } else if (aMethod === 'PUT') {
        await axios.put(fullurl, formData).then(success).catch(failure)
      } else if (aMethod === 'DELETE') {
        await axios.delete(fullurl).then(success).catch(failure)
      } else {
        throw new LucteriosException(GRAVE, Singleton().getTranslate('method unknown!'), aWebFile)
      }
    } finally {
      this.waitingOff()
    }
    return reponsetext
  }

  close () {
    if (this.getSessionEx() !== '') {
      var act = Singleton().CreateAction()
      if (act !== null) {
        act.initializeEx(null, Singleton().Factory(), '', 'CORE', 'exitConnection')
        act.actionPerformed()
      }
    }
    return super.close()
  }

  async getFileContent (aUrl, callback) {
    this.waitingOn()
    try {
      await axios.post(this.getServerUrl() + aUrl, null, {responseType: 'blob'}).then(function (data) {
        callback(data)
      }).catch(function (error) {
        console.log('HTTP ERROR:' + error)
      })
    } finally {
      this.waitingOff()
    }
  }
}

export class HttpTransportLocal extends HttpTransportAbstract {
  getIconUrl (icon) {
    var iconList = icon.split('/')
    return 'images/' + iconList[iconList.length - 1]
  }
}
