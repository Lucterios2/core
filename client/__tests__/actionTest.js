'use strict'
import { HashMap } from '../src/utils.js'
import { ActionImpl, SELECT_NONE, SELECT_SINGLE, FORM_MODAL, FORM_NOMODAL } from '../src/action.js'
import { Singleton } from '../src/singleton.js'
import { ObserverStub, ObserverFactoryMock, HttpTransportStub } from './mock.js'

var mAction = null

beforeEach(() => {
  mAction = new ActionImpl()
  Singleton().setHttpTransportClass(HttpTransportStub)
  ObserverStub.mParameters = new HashMap()
  ObserverStub.mLastActionId = ""
  ObserverStub.mLastSelect = SELECT_NONE
  ObserverStub.mShow = false
  ObserverStub.mTitle = ""
  ObserverFactoryMock.LastExtension = ""
  ObserverFactoryMock.LastAction = ""
  ObserverFactoryMock.LastParam = null
})

afterEach(() => {
  Singleton().close()
})

describe('Action', () => {
  if("Empty", () => {
    var action = {}
    mAction.initialize(null, null, action)

    expect(mAction.getTitle()).toEqual("")
    expect(mAction.getExtension()).toEqual("")
    expect(mAction.getAction()).toEqual("")
    expect(mAction.getIcon()).toEqual("")
    expect(mAction.getFormType()).toEqual(FORM_NOMODAL)
    expect(mAction.getClose()).toEqual(true)
    expect(mAction.getSelect()).toEqual(SELECT_NONE)
  })

  it("Action", () => {
    var action = {
      id : "CORE/usersEdit",
      modal : "1",
      icon : "/static/lucterios.CORE/images/edit.png",
      params : null,
      close : "0",
      text : "Modifier",
      action : "usersEdit",
      extension : "CORE",
      unique : "1"
    }
    mAction.initialize(null, null, action)
    expect(mAction.getTitle()).toEqual("Modifier")
    expect(mAction.getID()).toEqual('CORE/usersEdit')
    expect(mAction.getExtension()).toEqual("CORE")
    expect(mAction.getAction()).toEqual("usersEdit")
    expect(mAction.getIcon()).toEqual("/static/lucterios.CORE/images/edit.png")
    expect(mAction.getFormType()).toEqual(FORM_MODAL)
    expect(mAction.getClose()).toEqual(false)
    expect(mAction.getSelect()).toEqual(SELECT_NONE)
    var act_params = mAction.getParameters()
    expect(act_params.size()).toEqual(0)
  })

  it("Menu", () => {
    var act_params, action = {
      id : "CORE/usersEdit",
      modal : "0",
      icon : "",
      close : "1",
      text : "Modifier",
      action : "usersEdit",
      extension : "CORE",
      unique : "1",
      params : {
        'aaa' : '123',
        'bbb' : '546'
      }
    }
    mAction.initialize(null, null, action)

    expect(mAction.getID()).toEqual("CORE/usersEdit")
    expect(mAction.getTitle()).toEqual("Modifier")
    expect(mAction.getExtension()).toEqual("CORE")
    expect(mAction.getAction()).toEqual("usersEdit")
    expect(mAction.getIcon()).toEqual("")
    expect(mAction.getFormType()).toEqual(FORM_NOMODAL)
    expect(mAction.getClose()).toEqual(true)
    expect(mAction.getSelect()).toEqual(SELECT_NONE)
    act_params = mAction.getParameters()
    expect(act_params.size()).toEqual(2)
    expect(act_params.get('aaa')).toEqual('123')
    expect(act_params.get('bbb')).toEqual('546')
  })

  it("Simple", async () => {
    var fact = new ObserverFactoryMock()
    ObserverFactoryMock.NewObserver = new ObserverStub()

    var action = {
      extension : 'CORE',
      action : 'changePassword',
      close : '0',
      modal : '1',
      text : 'Modifier',
      id : 'CORE/changePasword',
      icon : "",
      params : null,
    }
    mAction.initialize(null, fact, action)
    await mAction.actionPerformed()

    expect(ObserverFactoryMock.LastExtension).toEqual("CORE")
    expect(ObserverFactoryMock.LastAction).toEqual("changePassword")
    expect(ObserverFactoryMock.LastParam.size()).toEqual(0)
    expect(ObserverStub.mShow).toEqual(true)
    expect(ObserverStub.mTitle).toEqual("Modifier")
    expect(ObserverFactoryMock.NewObserver.getGUI() == null).toEqual(true)
  })

  it("CloseParent", async () => {
    var obs_parent = new ObserverStub()
    ObserverStub.mParameters.put("abc", "123")

    var fact = new ObserverFactoryMock()
    ObserverFactoryMock.NewObserver = new ObserverStub()

    var action = {
      extension : 'CORE',
      action : 'changePassword',
      close : '1',
      modal : '1',
      text : 'Modifier',
      id : 'CORE/changePasword',
      icon : "",
      params : null,
    }
    mAction.initialize(obs_parent, fact, action)
    await mAction.actionPerformed()

    expect(ObserverFactoryMock.LastExtension).toEqual("CORE")
    expect(ObserverFactoryMock.LastAction).toEqual("changePassword")
    expect(ObserverFactoryMock.LastParam.size()).toEqual(1)
    expect(ObserverFactoryMock.LastParam.get("abc")).toEqual("123")
    expect(mAction.getClose()).toEqual(true)
    expect(mAction.getSelect()).toEqual(SELECT_NONE)
    expect(ObserverStub.mShow).toEqual(true)
    expect(ObserverStub.mTitle).toEqual("Modifier")
    expect(ObserverFactoryMock.NewObserver.getParent() == null).toEqual(true)

    expect(obs_parent.mClose).toEqual(true)
    expect(ObserverStub.mLastSelect).toEqual(SELECT_NONE)
  })

  it("NoCloseParent", async () => {
    var obs_parent = new ObserverStub()
    ObserverStub.mParameters.put("xyz", "456")
    ObserverStub.mParameters.put("ijk", "987")

    var fact = new ObserverFactoryMock()
    ObserverFactoryMock.NewObserver = new ObserverStub()

    var action = {
      extension : 'CORE',
      action : 'changePassword',
      close : '0',
      modal : '1',
      unique : '0',
      text : 'Modifier',
      id : 'CORE/changePasword',
      icon : "",
      params : null,
    }
    mAction.initialize(obs_parent, fact, action)
    await mAction.actionPerformed()

    expect(ObserverFactoryMock.LastExtension).toEqual("CORE")
    expect(ObserverFactoryMock.LastAction).toEqual("changePassword")
    expect(ObserverFactoryMock.LastParam.size()).toEqual(2)
    expect(ObserverFactoryMock.LastParam.get("xyz")).toEqual("456")
    expect(ObserverFactoryMock.LastParam.get("ijk")).toEqual("987")
    expect(mAction.getClose()).toEqual(false)
    expect(mAction.getSelect()).toEqual(SELECT_SINGLE)
    expect(ObserverStub.mShow).toEqual(true)
    expect(ObserverStub.mTitle).toEqual("Modifier")
    expect(ObserverFactoryMock.NewObserver.getParent() == obs_parent).toEqual(true)

    expect(!obs_parent.mClose).toEqual(true)
  })

  it("OnlyCloseParent", () => {
    var obs_parent = new ObserverStub()
    ObserverStub.mParameters.put("abc", "123")

    var fact = new ObserverFactoryMock()
    ObserverFactoryMock.NewObserver = null

    var action = {
      close : '1',
      modal : '0',
      text : 'Close',
      id : 'CORE/changePasword',
      icon : "",
      params : null,
    }
    mAction.initialize(obs_parent, fact, action)
    mAction.actionPerformed()

    expect(ObserverFactoryMock.LastExtension).toEqual("")
    expect(ObserverFactoryMock.LastAction).toEqual("")
    expect(ObserverFactoryMock.LastParam).toEqual(null)
    expect(mAction.getClose()).toEqual(true)
    expect(mAction.getFormType()).toEqual(FORM_NOMODAL)
    expect(mAction.getSelect()).toEqual(SELECT_NONE)
    expect(!ObserverStub.mShow).toEqual(true)
    expect(ObserverStub.mTitle).toEqual("")

    expect(obs_parent.mClose).toEqual(true)
  })
})
