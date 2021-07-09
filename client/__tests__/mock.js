'use strict'
import { HashMap, postLog } from '../src/utils.js'
import { HttpTransportAbstract } from '../src/transport.js'
import { ObserverFactoryAbstract } from '../src/observer_factory.js'
import { ObserverAbstract } from '../src/observer.js'
import { ObserverAcknowledge } from '../src/observer.acknowledge.js'
const $ = require('jquery')
const Blob = require('node-blob')
const util = require('util')

export class HttpTransportStub extends HttpTransportAbstract {
  constructor () {
    super()
    this.JSONReceive = ''
    this.XmlParam = new HashMap()
  }
  getIconUrl (icon) {
    return 'STUB/' + icon
  }
  async transfertFileFromServerString (aWebFile, aParams) {
    var self = this
    this.XmlParam['WebFile'] = aWebFile
    aParams.keys().forEach(function(key) {
      self.XmlParam[key] = decodeURIComponent(aParams.get(key))
    })
    return this.JSONReceive
  }
  getFileContent (aUrl, callback) {
    this.XmlParam['URL'] = aUrl
    callback(new Blob([ this.JSONReceive ], {
	  type : "text/plain;charset=UTF-8"
	}))
  }
}

export class ObserverFactoryMock extends ObserverFactoryAbstract {
  constructor () {
    super()
    this.CallList = new HashMap()
  }
  init () {
	this.CallList = new HashMap()
  }
  async callAction (aExtension, aAction, aParam, aObserver) {
    var new_call, new_param = new HashMap()
    aParam.keys().forEach(function(key) {
      var val = aParam.get(key)
      if (typeof val === 'string') {
        new_param[key] = val
      }
    })
    new_call = util.format("%s->%s(%s)", aExtension, aAction, new_param.toString())
    this.CallList.put(this.CallList.size(), new_call)
    postLog('*** callAction:' + new_call)
    ObserverFactoryMock.LastExtension = aExtension
    ObserverFactoryMock.LastAction = aAction
    ObserverFactoryMock.LastParam = aParam
    return ObserverFactoryMock.NewObserver
  }
}
ObserverFactoryMock.LastExtension = ""
ObserverFactoryMock.LastAction = ""
ObserverFactoryMock.LastParam = null
ObserverFactoryMock.NewObserver = null

export class ObserverStub extends ObserverAbstract {
  constructor () {
	super()
	this.mClose = false
  }
  getObserverName () {
    return ObserverStub.ObserverName
  }
  show (aTitle) {
    ObserverStub.mShow = true
    ObserverStub.mTitle = aTitle
  }
  getParameters (aCheckNull) {
    ObserverStub.mLastCheckNull = aCheckNull
    return ObserverStub.mParameters
  }
  close (aMustRefreshParent) {
    this.mClose = true
    if (this.getGUI() != null) {
      this.getGUI().setVisible(false)
    }
    super.close(aMustRefreshParent)
  }
}
ObserverStub.ObserverName = "ObserverStub"
ObserverStub.mParameters = new HashMap()
ObserverStub.mLastCheckNull = false
ObserverStub.mShow = false
ObserverStub.mTitle = ""


export class ObserverAcknowledgeNoParent extends ObserverAcknowledge {
  setParent (aParent) {
    this.mParent = null
  }
}

export class UIMock {
  constructor () {
	this.optionsDialog = []
	this.optionsTabs = []
	this.optionsAccordion = []
	this.optionsSpinner = []
	$.fn.dialog = jest.fn()	  
	$.fn.tabs = jest.fn()
	$.fn.accordion = jest.fn()
	$.fn.spinner = jest.fn()
  }
  
  clean () {
	this.optionsDialog = []
	this.optionsTabs = []
	this.optionsAccordion = []
	this.optionsSpinner = []
    $.fn.dialog.mockClear()
    $.fn.dialog.mockImplementation((option) => {
  	  this.optionsDialog.push(option)
    })
    $.fn.tabs.mockClear()
    $.fn.tabs.mockImplementation((option) => {
  	  this.optionsTabs.push(option)
    })
    $.fn.accordion.mockClear()
    $.fn.accordion.mockImplementation((option) => {
  	  this.optionsAccordion.push(option)
    })
    $.fn.spinner.mockClear()
    $.fn.spinner.mockImplementation((option) => {
  	  this.optionsSpinner.push(option)
    })
  }
  getTextButton(dlgNum, btnNum) {
	return this.optionsDialog[dlgNum].buttons[btnNum].text
  }
  buttonCount(dlgNum) {
	return this.optionsDialog[dlgNum].buttons.length
  }
  async clickButton(dlgNum, btnNum) {
	await this.optionsDialog[dlgNum].buttons[btnNum].click()
  }
}