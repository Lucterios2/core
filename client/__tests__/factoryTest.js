'use strict'
/* global beforeEach, afterEach, describe, it, expect */
import { HashMap } from '../src/utils.js'
import { Singleton, SingletonClose } from '../src/singleton.js'
import { ObserverStub, HttpTransportStub } from './mock.js'
import { ObserverFactoryRestImpl } from '../src/observer_factory.js'
import { ActionImpl } from '../src/action.js'

var mHttpTransport = null
var mObserverFactory = null

beforeEach(() => {
  Singleton().setActionClass(ActionImpl)
  ObserverStub.ObserverName = 'ObserverStub'
  mHttpTransport = new HttpTransportStub()
  mObserverFactory = new ObserverFactoryRestImpl()
  mObserverFactory.setHttpTransport(mHttpTransport)
  mObserverFactory.clearObserverList()

  mObserverFactory.AddObserver('core.auth', ObserverStub)
  mObserverFactory.AddObserver('Core.Menu', ObserverStub)
  mObserverFactory.AddObserver('core.dialogbox', ObserverStub)
  mObserverFactory.AddObserver('core.custom', ObserverStub)
})

afterEach(() => {
  mHttpTransport.close()
  mHttpTransport = null
  SingletonClose()
})

describe('ObserverFactoryRest', () => {
  it('CallAction', async () => {
    mHttpTransport.JSONReceive = {
      'context': {
        'personneMorale': '100',
        'CONFIRME': 'YES',
        'bidule': 'aaa'
      },
      'actions': [ {
        'params': {
          'CONFIRME': 'YES'
        },
        'icon': '/static/lucterios.CORE/images/ok.png',
        'close': '0',
        'unique': '1',
        'extension': 'lucterios.dummy',
        'text': 'Oui',
        'modal': '1',
        'id': 'lucterios.dummy/multi',
        'action': 'multi'
      }, {
        'unique': '1',
        'id': '',
        'close': '1',
        'icon': '/static/lucterios.CORE/images/cancel.png',
        'text': 'Non',
        'modal': '1',
        'params': null
      } ],
      'close': null,
      'data': {
        'text': 'Do you want?',
        'type': 2
      },
      'meta': {
        'extension': 'lucterios.dummy',
        'title': 'Confirmation',
        'action': 'multi',
        'observer': 'core.dialogbox'
      }
    }

    var currentParams = new HashMap()
    var obs = await mObserverFactory.callAction('lucterios.dummy', 'multi', currentParams, null)
    expect(obs != null).toEqual(true)
    expect(obs.getSourceAction()).toEqual('multi')
    expect(obs.getSourceExtension()).toEqual('lucterios.dummy')
    expect(obs.getContext().size()).toEqual(3)
    expect(obs.getContext().get('personneMorale')).toEqual('100')
    expect(obs.getContext().get('CONFIRME')).toEqual('YES')
    expect(obs.getContext().get('bidule')).toEqual('aaa')
    expect(obs.getTitle()).toEqual('Confirmation')

    expect(mHttpTransport.XmlParam.size()).toEqual(1)
    expect(mHttpTransport.XmlParam['WebFile']).toEqual('lucterios.dummy/multi')
  })

  it('Refresh', async () => {
    ObserverStub.ObserverName = 'core.dialogbox'
    mHttpTransport.JSONReceive = {
      'context': {
        'personneMorale': '100',
        'bidule': 'aaa'
      },
      'actions': [ {
        'params': {
          'CONFIRME': 'YES'
        },
        'icon': '/static/lucterios.CORE/images/ok.png',
        'close': '0',
        'unique': '1',
        'extension': 'lucterios.dummy',
        'text': 'Oui',
        'modal': '1',
        'id': 'lucterios.dummy/multi',
        'action': 'multi'
      }, {
        'unique': '1',
        'id': '',
        'close': '1',
        'icon': '/static/lucterios.CORE/images/cancel.png',
        'text': 'Non',
        'modal': '1',
        'params': null
      } ],
      'close': null,
      'data': {
        'text': 'Do you want?',
        'type': 2
      },
      'meta': {
        'extension': 'lucterios.dummy',
        'title': 'Réinitialisation',
        'action': 'multi',
        'observer': 'core.dialogbox'
      }
    }

    var obs = new ObserverStub()
    obs.setSource('lucterios.dummy', 'multi')
    obs.setContent(null)
    obs.mContext = new HashMap()
    obs.mContext.put('CONFIRME', 'YES')

    await mObserverFactory.callAction(obs.getSourceExtension(), obs.getSourceAction(), obs.getContext(), obs)

    expect(obs.getSourceAction()).toEqual('multi')
    expect(obs.getSourceExtension()).toEqual('lucterios.dummy')
    expect(obs.getContext().size()).toEqual(2)
    expect(obs.getContext().get('personneMorale')).toEqual('100')
    expect(obs.getContext().get('bidule')).toEqual('aaa')
    expect(obs.getTitle()).toEqual('Réinitialisation')

    expect(mHttpTransport.XmlParam.size()).toEqual(2)
    expect(mHttpTransport.XmlParam['WebFile']).toEqual('lucterios.dummy/multi')
    expect(mHttpTransport.XmlParam['CONFIRME']).toEqual('YES')
  })

  it('CallActionWithParam', async () => {
    mHttpTransport.JSONReceive = {
      'context': {
        'personneMorale': '100',
        'CONFIRME': 'YES',
        'bidule': 'aaa'
      },
      'actions': [ {
        'params': {
          'CONFIRME': 'YES'
        },
        'icon': '/static/lucterios.CORE/images/ok.png',
        'close': '0',
        'unique': '1',
        'extension': 'lucterios.dummy',
        'text': 'Oui',
        'modal': '1',
        'id': 'lucterios.dummy/multi',
        'action': 'multi'
      }, {
        'unique': '1',
        'id': '',
        'close': '1',
        'icon': '/static/lucterios.CORE/images/cancel.png',
        'text': 'Non',
        'modal': '1',
        'params': null
      } ],
      'close': null,
      'data': {
        'text': 'Do you want?',
        'type': 2
      },
      'meta': {
        'extension': 'lucterios.dummy',
        'title': 'Réinitialisation',
        'action': 'multi',
        'observer': 'core.dialogbox'
      }
    }

    var params = new HashMap()
    params.put('print_model', '107')
    params.put('CONFIRME', 'YES')
    var obs = await mObserverFactory.callAction('lucterios.dummy', 'multi', params, null)
    expect(obs.getObserverName()).toEqual('ObserverStub')

    expect(mHttpTransport.XmlParam.size()).toEqual(3)
    expect(mHttpTransport.XmlParam['WebFile']).toEqual('lucterios.dummy/multi')
    expect(mHttpTransport.XmlParam['print_model']).toEqual('107')
    expect(mHttpTransport.XmlParam['CONFIRME']).toEqual('YES')
  })

  it('CallActionBadXmlReceived', async () => {
    mHttpTransport.XmlReceved = 'Error php in truc.inc.php line 123'
    try {
      await mObserverFactory.callAction('CORE', 'printmodelReinit', new HashMap())
      expect(true).toEqual(false)
    } catch (err) {
      expect(err.message).toEqual('Erreur inconnu')
    }
  })

  it('CallActionBadObserver', async () => {
    mHttpTransport.JSONReceive = {
      'context': {
        'personneMorale': '100',
        'CONFIRME': 'YES',
        'bidule': 'aaa'
      },
      'actions': [],
      'close': null,
      'data': {
        'text': 'Do you want?',
        'type': 2
      },
      'meta': {
        'extension': 'lucterios.dummy',
        'title': 'Réinitialisation',
        'action': 'multi',
        'observer': 'core.dialbox'
      }
    }
    try {
      var obs = await mObserverFactory.callAction('lucterios.dummy', 'multi', new HashMap())
      expect(obs).toEqual(null)
      expect(true).toEqual(false)
    } catch (err) {
      expect(err.message).toEqual('Observeur \'core.dialbox\' inconnu.')
    }
  })

  it('Authentification needauth', async () => {
    ObserverStub.ObserverName = 'core.auth'
    mHttpTransport.JSONReceive = {
      'close': null,
      'context': {},
      'data': 'NEEDAUTH',
      'meta': {
        'title': 'info',
        'action': 'authentification',
        'observer': 'core.auth',
        'extension': 'CORE'
      }
    }
    expect(await mObserverFactory.setAuthentification('abc', '123')).toEqual(false)
    expect(mHttpTransport.getSession()).toEqual('')
    expect(mHttpTransport.XmlParam.size()).toEqual(3)
    expect(mHttpTransport.XmlParam['WebFile']).toEqual('CORE/authentification')
    expect(mHttpTransport.XmlParam['login']).toEqual('abc')
    expect(mHttpTransport.XmlParam['password']).toEqual('123')
  })

  it('Authentification ok', async () => {
    ObserverStub.ObserverName = 'core.auth'
    mHttpTransport.JSONReceive = {
      'connexion': {
        'SUPPORT_EMAIL': 'support@lucterios.org',
        'VERSION': '2.1.1.16062115',
        'SERVERVERSION': '2.1.15.17102417',
        'REALNAME': 'Administrateur ',
        'COPYRIGHT': '(c) 2015 lucterios.org - GPL Licence',
        'MODE': '0',
        'LOGIN': 'admin',
        'LOGONAME': 'http://demo.lucterios.org/Lucterios/extensions/applis/images/logo.gif',
        'LANGUAGE': 'fr',
        'INSTANCE': 'dev',
        'SUPPORT_HTML': '',
        'INFO_SERVER': [ 'C\u0153ur Lucterios=2.1.15.17102417', 'Lucterios standard=2.1.1.16062115', '',
          '{[i]}Linux x86_64 3.19.0-32-generic - Python 3.4.3 - Django 1.10.4{[/i]}' ],
        'SUBTITLE': 'Application g\u00e9n\u00e9rique de gestion',
        'TITLE': 'Lucterios standard',
        'EMAIL': 'Support Lucterios <support@lucterios.org>',
        'BACKGROUND': ''
      },
      'close': null,
      'context': {
        'login': 'admin',
        'ses': 'admin1315821586',
        'password': 'admin'
      },
      'data': 'OK',
      'meta': {
        'title': 'info',
        'action': 'authentification',
        'observer': 'core.auth',
        'extension': 'CORE'
      }
    }
    expect(await mObserverFactory.setAuthentification('admin', 'admin')).toEqual(true)
    expect(mHttpTransport.getSession()).toEqual('admin1315821586')

    expect(mHttpTransport.XmlParam.size()).toEqual(3)
    expect(mHttpTransport.XmlParam['WebFile']).toEqual('CORE/authentification')
    expect(mHttpTransport.XmlParam['login']).toEqual('admin')
    expect(mHttpTransport.XmlParam['password']).toEqual('admin')
  })

  it('Authentification session', async () => {
    ObserverStub.ObserverName = 'core.auth'
    mHttpTransport.JSONReceive = {
      'connexion': {
        'SUPPORT_EMAIL': 'support@lucterios.org',
        'VERSION': '2.1.1.16062115',
        'SERVERVERSION': '2.1.15.17102417',
        'REALNAME': 'Administrateur ',
        'COPYRIGHT': '(c) 2015 lucterios.org - GPL Licence',
        'MODE': '0',
        'LOGIN': 'admin',
        'LOGONAME': 'http://demo.lucterios.org/Lucterios/extensions/applis/images/logo.gif',
        'LANGUAGE': 'fr',
        'INSTANCE': 'dev',
        'SUPPORT_HTML': '',
        'INFO_SERVER': [ 'C\u0153ur Lucterios=2.1.15.17102417', 'Lucterios standard=2.1.1.16062115', '',
          '{[i]}Linux x86_64 3.19.0-32-generic - Python 3.4.3 - Django 1.10.4{[/i]}' ],
        'SUBTITLE': 'Application g\u00e9n\u00e9rique de gestion',
        'TITLE': 'Lucterios standard',
        'EMAIL': 'Support Lucterios <support@lucterios.org>',
        'BACKGROUND': ''
      },
      'close': null,
      'context': {
        'ses': 'admin1315821586'
      },
      'data': 'OK',
      'meta': {
        'title': 'info',
        'action': 'authentification',
        'observer': 'core.auth',
        'extension': 'CORE'
      }
    }
    expect(await mObserverFactory.setAuthentification(null, 'admin1315821586')).toEqual(true)
    expect(mHttpTransport.getSession()).toEqual('admin1315821586')

    expect(mHttpTransport.XmlParam.size()).toEqual(3)
    expect(mHttpTransport.XmlParam['WebFile']).toEqual('CORE/authentification')
    expect(mHttpTransport.XmlParam['ses']).toEqual('admin1315821586')
    expect(mHttpTransport.XmlParam['info']).toEqual('1')
  })
})
