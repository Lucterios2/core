'use strict'
/* global beforeEach, afterEach, describe, it, expect */
import { Singleton, SingletonClose, setInitialCallBack } from '../src/singleton.js'
import { ObserverFactoryMock, HttpTransportStub, UIMock } from './mock.js'
import { ActionImpl } from '../src/action.js'
import { ApplicationDescription, ObserverAuthentification } from '../src/observer.authentification.js'
import { ObserverAcknowledge } from '../src/observer.acknowledge.js'
import { ObserverException } from '../src/observer.exception.js'
import { ObserverPrint, MODE_EXPORT_CSV } from '../src/observer.print.js'
import { ObserverDialogBox } from '../src/observer.dialogbox.js'
const $ = require('jquery')
const atob = require('atob')
const html = require('fs').readFileSync('./index.html').toString()
const currentUI = new UIMock()

var mFileContent = null
var mFileName = null
var mCalled = 0
var mObsFactory = null

beforeEach(() => {
  document.body.innerHTML = html
  mCalled = 0
  mObsFactory = new ObserverFactoryMock()

  Singleton().setHttpTransportClass(HttpTransportStub)
  Singleton().setFactory(mObsFactory)
  Singleton().setActionClass(ActionImpl)
  Singleton().Transport().setSession('abc123')
  Singleton().Transport().setLastLogin('admin')
  Singleton().mSelectLang = 'fr'
  mObsFactory.setHttpTransport(Singleton().Transport())

  ObserverFactoryMock.NewObserver = new ObserverAcknowledge()
  setInitialCallBack(callback)
})

afterEach(() => {
  ObserverAuthentification.connectSetValue = null
  setInitialCallBack(null)
  SingletonClose()
})

var saveFile = function (aContent, aFileName) {
  mFileContent = atob(aContent)
  mFileName = aFileName
}

var callback = function () {
  mCalled++
}

describe('Observer', () => {
  it('Authentification 1', () => {
    Singleton().Transport().setSession('')
    var jsonReceive = {
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
        'INFO_SERVER': [ 'C\u0153ur Lucterios=2.1.15.17102417', 'Lucterios standard=2.1.1.16062115', '', '{[i]}Linux x86_64 3.19.0-32-generic - Python 3.4.3 - Django 1.10.4{[/i]}' ],
        'SUBTITLE': 'Application g\u00e9n\u00e9rique de gestion',
        'TITLE': 'Lucterios standard',
        'EMAIL': 'Support Lucterios <support@lucterios.org>',
        'BACKGROUND': ''
      },
      'close': null,
      'context': {
        'username': 'admin',
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
    var obs = new ObserverAuthentification()
    obs.setSource('CORE', 'Auth')
    obs.setContent(jsonReceive)
    obs.show('Mon titre')
    expect(obs.getGUI()).toEqual(null)
    var description = Singleton().mDesc
    expect(description.getTitle()).toEqual('Lucterios standard')
    expect(description.getApplisVersion()).toEqual('2.1.1.16062115')
    expect(description.getServerVersion()).toEqual('2.1.15.17102417')
    expect(description.getCopyRigth()).toEqual('(c) 2015 lucterios.org - GPL Licence')
    expect(description.getLogoIconName()).toEqual('http://demo.lucterios.org/Lucterios/extensions/applis/images/logo.gif')
    expect(description.getInfoServer()).toEqual('Cœur Lucterios=2.1.15.17102417{[br/]}Lucterios standard=2.1.1.16062115{[br/]}{[br/]}{[i]}Linux x86_64 3.19.0-32-generic - Python 3.4.3 - Django 1.10.4{[/i]}')
    expect(description.getSupportEmail()).toEqual('Support Lucterios <support@lucterios.org>')
    expect(description.getSubTitle()).toEqual('Application générique de gestion')
    expect(description.getLogin()).toEqual('admin')
    expect(description.getRealName()).toEqual('Administrateur')
    expect(Singleton().mRefreshMenu).toEqual(true)
    expect(obs.getRefreshMenu()).toEqual(false)
    expect(Singleton().Transport().getSession()).toEqual('admin1315821586')
  })

  it('Authentification 2', async () => {
    var jsonReceive = {
      'close': null,
      'context': {
        'username': 'admin',
        'password': 'abc123'
      },
      'actions': [ {
        'unique': '1',
        'icon': '/static/lucterios.CORE/images/passwd.png',
        'action': 'askPassword',
        'close': '0',
        'extension': 'CORE',
        'text': 'Mot de passe ou alias oubli\u00e9?',
        'params': null,
        'id': 'CORE/askPassword',
        'modal': '1'
      } ],
      'data': 'BADAUTH',
      'meta': {
        'title': 'info',
        'action': 'authentification',
        'observer': 'core.auth',
        'extension': 'CORE'
      }
    }
    currentUI.clean()

    var obs = new ObserverAuthentification()
    obs.setSource('CORE', 'authentification')
    obs.setContent(jsonReceive)
    obs.show('Connexion')

    var gui = obs.getGUI()
    expect(gui != null).toEqual(true)
    expect(gui.isExist()).toEqual(true)

    var jcnt = gui.getHtmlDom()

    var lbl = jcnt.find('table:eq(0) > tbody > tr:eq(0) > td:eq(0) > label')
    expect(lbl.text()).toEqual('Alias ou Mot de passe incorrect!')

    lbl = jcnt.find('table:eq(0) > tbody > tr:eq(1) > td:eq(0) > span')
    expect(lbl.html()).toEqual('<b>Alias</b>')

    lbl = jcnt.find('table:eq(0) > tbody > tr:eq(1) > td:eq(1) > input')
    expect(lbl.val()).toEqual('')
    lbl.val('machin')

    lbl = jcnt.find('table:eq(0) > tbody > tr:eq(2) > td:eq(0) > span')
    expect(lbl.html()).toEqual('<b>Mot de passe</b>')

    lbl = jcnt.find('table:eq(0) > tbody > tr:eq(2) > td:eq(1) > input')
    expect(lbl.val()).toEqual('')
    lbl.val('coucou')

    expect($.fn.dialog).toHaveBeenCalledTimes(3)
    expect(currentUI.optionsDialog.length).toBe(3)
    expect(currentUI.buttonCount(0)).toEqual(3)
    expect(currentUI.getTextButton(0, 0)).toEqual('Ok')
    expect(currentUI.getTextButton(0, 1)).toEqual('Les serveurs')
    expect(currentUI.getTextButton(0, 2)).toEqual('Annuler')

    expect(mObsFactory.CallList.size()).toEqual(0)

    await currentUI.clickButton(0, 0)

    expect(!gui.isExist()).toEqual(true)
    expect(mObsFactory.CallList.size()).toEqual(1)
    expect(mObsFactory.CallList.get(0)).toEqual('CORE->authentification(username=\'machin\',password=\'coucou\',)')
  })

  it('Authentification 3', async () => {
    var jsonReceive = {
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
    currentUI.clean()
    expect(mCalled).toEqual(0)

    var obs = new ObserverAuthentification()
    obs.setSource('CORE', 'authentification')
    obs.setContent(jsonReceive)
    obs.show('Connexion')

    expect(mCalled).toEqual(1)

    var gui = obs.getGUI()
    expect(gui != null).toEqual(true)
    expect(gui.isExist()).toEqual(true)

    var jcnt = gui.getHtmlDom()

    var lbl = jcnt.find('table:eq(0) > tbody > tr:eq(0) > td:eq(0) > label')
    expect(lbl.text()).toEqual('Veuillez vous identifier')

    expect($.fn.dialog).toHaveBeenCalledTimes(3)
    expect(currentUI.optionsDialog.length).toBe(3)
    expect(currentUI.buttonCount(0)).toEqual(3)
    expect(currentUI.getTextButton(0, 0)).toEqual('Ok')
    expect(currentUI.getTextButton(0, 1)).toEqual('Les serveurs')
    expect(currentUI.getTextButton(0, 2)).toEqual('Annuler')

    Singleton().mDesc = 0
    expect(mObsFactory.CallList.size()).toEqual(0)
    expect(mCalled).toEqual(1)

    await currentUI.clickButton(0, 2)

    expect(!gui.isExist()).toEqual(true)
    expect(mObsFactory.CallList.size()).toEqual(0)

    expect(mCalled).toEqual(2)
    expect(Singleton().mDesc).toEqual(null)
  })

  it('Acknowledge', () => {
    var jsonReceive = {
      'close': {
        'params': null,
        'id': 'CORE/unlock',
        'unique': '1',
        'modal': '1',
        'text': 'unlock',
        'action': 'unlock',
        'extension': 'CORE',
        'close': '1'
      },
      'action': {
        'params': null,
        'id': 'toto/bidule',
        'unique': '1',
        'modal': '1',
        'text': '',
        'action': 'bidule',
        'extension': 'toto',
        'close': '1'
      },
      'context': {
        'LOCK_IDENT': 'lucterios.CORE.models-LucteriosGroup-1',
        'group': '1'
      },
      'meta': {
        'title': '',
        'action': 'groupsEdit',
        'observer': 'core.acknowledge',
        'extension': 'CORE'
      }
    }
    currentUI.clean()

    var obs = new ObserverAcknowledge()
    obs.setSource('CORE', 'groupsEdit')
    obs.setContent(jsonReceive)
    obs.show('Mon titre')

    expect(obs.getGUI() == null).toEqual(true)

    expect(obs.getContext().size()).toEqual(2)
    expect(obs.getContext().get('group')).toEqual('1')

    expect(obs.getRedirectAction() != null).toEqual(true)
    expect(obs.getRedirectAction().getExtension()).toEqual('toto')
    expect(obs.getRedirectAction().getAction()).toEqual('bidule')

    expect($.fn.dialog).toHaveBeenCalledTimes(0)

    expect(mObsFactory.CallList.size()).toEqual(2)
    expect(mObsFactory.CallList.get(0)).toEqual('CORE->unlock(LOCK_IDENT=\'lucterios.CORE.models-LucteriosGroup-1\',group=\'1\',)')
    expect(mObsFactory.CallList.get(1)).toEqual('toto->bidule(LOCK_IDENT=\'lucterios.CORE.models-LucteriosGroup-1\',group=\'1\',)')
  })

  it('Exception1', () => {
    Singleton().mDesc = new ApplicationDescription('aa', 'bb', 'cc', 'dd', 'ee')
    var jsonReceive = {
      'context': {},
      'close': null,
      'exception': {
        'message': 'Critique',
        'debug': '/usr/local/lib/python3.4/site-packages/django/views/generic/base.py in line 88 in dispatch: return handler(request, *args, **kwargs){[br/]}/home/dev/Lucterios2/lct-core/lucterios/framework/xferbasic.py in line 332 in get: return self.get_post(request, *args, **kwargs){[br/]}/home/dev/Lucterios2/lct-core/lucterios/framework/xfergraphic.py in line 159 in get_post: self.fillresponse(**self._get_params()){[br/]}/home/dev/Lucterios2/lct-core/lucterios/dummy/views.py in line 55 in fillresponse: raise LucteriosException(GRAVE, \'Error of bidule\'){[br/]}',
        'code': '1',
        'type': 'LucteriosException'
      },
      'meta': {
        'extension': 'lucterios.dummy',
        'title': '',
        'action': 'bidule',
        'observer': 'core.exception'
      }
    }
    currentUI.clean()

    var obs = new ObserverException()
    obs.setSource('CORE', 'validerAct')
    obs.setContent(jsonReceive)
    obs.show('Mon titre')

    var gui = obs.getGUI()
    expect(gui != null).toEqual(true)
    expect(gui.isExist()).toEqual(true)

    var jcnt = gui.getHtmlDom()
    var img = jcnt.find('table:eq(0) > tbody > tr:eq(0) > td:eq(0) > img')
    expect(img.attr('src').substr(-9)).toEqual('error.png')

    var lbl = jcnt.find('table:eq(0) > tbody > tr:eq(0) > td:eq(1) > label')
    expect(lbl.text()).toEqual('Critique')

    var btn1 = jcnt.find('table:eq(0) > tbody > tr:eq(1) > td:eq(0) > input[name=\'info\']')
    expect(btn1.attr('value')).toEqual('>>')
    expect(btn1.attr('type')).toEqual('button')
    var btn2 = jcnt.find('table:eq(0) > tbody > tr:eq(1) > td:eq(0) > input[name=\'send\']')
    expect(btn2.attr('value')).toEqual('Envoyer au support')
    expect(btn2.attr('type')).toEqual('button')

    var memo = jcnt.find('table:eq(0) > tbody > tr:eq(2) > td:eq(0) > div > div > pre')
    expect(memo.text()).toEqual('/usr/local/lib/python3.4/site-packages/django/views/generic/base.py in line 88 in dispatch: return handler(request, *args, **kwargs)\n' +
      '/home/dev/Lucterios2/lct-core/lucterios/framework/xferbasic.py in line 332 in get: return self.get_post(request, *args, **kwargs)\n' +
      '/home/dev/Lucterios2/lct-core/lucterios/framework/xfergraphic.py in line 159 in get_post: self.fillresponse(**self._get_params())\n' +
      '/home/dev/Lucterios2/lct-core/lucterios/dummy/views.py in line 55 in fillresponse: raise LucteriosException(GRAVE, \'Error of bidule\')')

    lbl = jcnt.find('table:eq(0) > tbody > tr:eq(2) > td:eq(0) > div > div > label')
    expect(lbl.text()).toEqual('LucteriosException')

    expect($.fn.dialog).toHaveBeenCalledTimes(1)
    expect(currentUI.optionsDialog.length).toBe(1)
    expect(currentUI.buttonCount(0)).toEqual(2)
    expect(currentUI.getTextButton(0, 0)).toEqual('Les serveurs')
    expect(currentUI.getTextButton(0, 1)).toEqual('Fermer')

    expect(mObsFactory.CallList.size()).toEqual(0)
    gui.close()
    expect(!gui.isExist()).toEqual(true)
  })

  it('Exception2', () => {
    var jsonReceive = {
      'exception': {
        'type': 'LucteriosException',
        'debug': '/usr/local/lib/python3.4/site-packages/django/views/generic/base.py in line 88 in dispatch: return handler(request, *args, **kwargs){[br/]}/home/dev/Lucterios2/lct-core/lucterios/framework/xferbasic.py in line 332 in get: return self.get_post(request, *args, **kwargs){[br/]}/home/dev/Lucterios2/lct-core/lucterios/framework/xferadvance.py in line 162 in get_post: self._initialize(request, *args, **kwargs){[br/]}/home/dev/Lucterios2/lct-core/lucterios/framework/xferbasic.py in line 260 in _initialize: self._search_model(){[br/]}/home/dev/Lucterios2/lct-core/lucterios/framework/xferbasic.py in line 172 in _search_model: self._load_unique_record(ids[0]){[br/]}/home/dev/Lucterios2/lct-core/lucterios/framework/xferbasic.py in line 160 in _load_unique_record: IMPORTANT, _(\'This record not exist!\\nRefresh your application.\')){[br/]}',
        'message': 'Mineur',
        'code': '4'
      },
      'close': null,
      'context': {
        'username': 'admin',
        'group': '50',
        'password': 'adms'
      },
      'meta': {
        'title': '',
        'action': 'groupsEdit',
        'observer': 'core.exception',
        'extension': 'CORE'
      }
    }
    currentUI.clean()

    var obs = new ObserverException()
    obs.setSource('CORE', 'groupsEdit')
    obs.setContent(jsonReceive)
    obs.show('Mon titre')

    var gui = obs.getGUI()
    expect(gui != null).toEqual(true)
    expect(gui.isExist()).toEqual(true)

    var jcnt = gui.getHtmlDom()
    var img = jcnt.find('table > tbody > tr:eq(0) > td:eq(0) > img')
    expect(img.attr('src').substr(-8)).toEqual('info.png')

    var lbl = jcnt.find('table > tbody > tr:eq(0) > td:eq(1) > label')
    expect(lbl.text()).toEqual('Mineur')

    var btn1 = jcnt.find('table:eq(0) > tbody > tr:eq(1) > td:eq(0) > input')
    expect(btn1.length).toEqual(0)
    var btn2 = jcnt.find('table:eq(0) > tbody > tr:eq(1) > td:eq(1) > input')
    expect(btn2.length).toEqual(0)

    var memo = jcnt.find('table:eq(0) > tbody > tr:eq(2) > td:eq(0) > div > div > pre')
    expect(memo.length).toEqual(0)

    lbl = jcnt.find('table:eq(0) > tbody > tr:eq(2) > td:eq(0) > div > div > label')
    expect(lbl.length).toEqual(0)

    expect($.fn.dialog).toHaveBeenCalledTimes(1)
    expect(currentUI.optionsDialog.length).toBe(1)
    expect(currentUI.buttonCount(0)).toEqual(2)
    expect(currentUI.getTextButton(0, 0)).toEqual('Les serveurs')
    expect(currentUI.getTextButton(0, 1)).toEqual('Fermer')

    expect(mObsFactory.CallList.size()).toEqual(0)
    gui.close()
    expect(!gui.isExist()).toEqual(true)
  })

  it('Print', () => {
    var jsonReceive = {
      'context': {
        'PRINT_MODE': '4',
        'example': '1'
      },
      'close': null,
      'print': {
        'title': 'Example d\'impression',
        'mode': 4,
        'content': 'CiAgICAgICJFeGFtcGxlIgogICAgCiAgICAgIAogICAgICAibmFtZSIKICAgICAgImFhYWEiCiAgICAgICJ2YWx1ZSIKICAgICAgIjUiCiAgICAgICJwcmljZSIKICAgICAgIjEwMC4wMCIKICAgICAgImRhdGUiCiAgICAgICItLS0iCiAgICAgICJ0aW1lIgogICAgICAiMDA6MDAiCiAgICAgICJ2YWxpZCIKICAgICAgIk5vbiIKICAgICAgImNvbW1lbnQiCiAgICAgICJxcXFxIgogICAgCg=='
      },
      'meta': {
        'extension': 'lucterios.dummy',
        'title': 'Example d\'impression',
        'action': 'examplePrint',
        'observer': 'core.print'
      }
    }

    Singleton().mFileManager.saveFile = saveFile
    expect(mFileContent).toEqual(null)
    var obs = new ObserverPrint()
    obs.setSource('lucterios.dummy', 'examplePrint')
    obs.setContent(jsonReceive)
    obs.show('Example d\'impression')

    expect(obs.getContext().size()).toEqual(2)
    expect(obs.getContext().get('example')).toEqual('1')
    expect(obs.getContext().get('PRINT_MODE')).toEqual('4')
    expect(obs.mode).toEqual(MODE_EXPORT_CSV)
    expect(obs.title).toEqual('Example d\'impression')

    expect(mFileContent != null).toEqual(true)
    var contents = mFileContent.split('\n')
    expect(contents.length).toEqual(20)
    expect(contents[1].trim()).toEqual('"Example"')
    expect(contents[4].trim()).toEqual('"name"')
    expect(contents[6].trim()).toEqual('"value"')
    expect(mFileName).toEqual('Example_d_impression.csv')
    expect(mObsFactory.CallList.size()).toEqual(0)
  })

  it('Dialog', async () => {
    var jsonReceive = {
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
    currentUI.clean()

    var obs = new ObserverDialogBox()
    obs.setSource('lucterios.dummy', 'multi')
    obs.setContent(jsonReceive)
    obs.show('multi')

    var gui = obs.getGUI()
    expect(gui != null).toEqual(true)
    expect(gui.isExist()).toEqual(true)

    var jcnt = gui.getHtmlDom()
    var img = jcnt.find('table:eq(0) > tbody > tr:eq(0) > td:eq(0) > img')
    expect(img.attr('src').substr(-11)).toEqual('confirm.png')

    var lbl = jcnt.find('table:eq(0) > tbody > tr:eq(0) > td:eq(1) > label')
    expect(lbl.text()).toEqual('Do you want?')

    expect($.fn.dialog).toHaveBeenCalledTimes(1)
    expect(currentUI.optionsDialog.length).toBe(1)
    expect(currentUI.buttonCount(0)).toEqual(2)
    expect(currentUI.getTextButton(0, 0)).toEqual('Oui')
    expect(currentUI.getTextButton(0, 1)).toEqual('Non')

    expect(obs.getContext().size()).toEqual(3)
    expect(obs.getContext().get('personneMorale')).toEqual('100')
    expect(obs.getContext().get('CONFIRME')).toEqual('YES')

    expect(mObsFactory.CallList.size()).toEqual(0)

    await currentUI.clickButton(0, 0)

    expect(gui.isExist()).toEqual(true)
    expect(mObsFactory.CallList.size()).toEqual(2)
    expect(mObsFactory.CallList.get(0)).toEqual('lucterios.dummy->multi(personneMorale=\'100\',CONFIRME=\'YES\',bidule=\'aaa\',)')
    expect(mObsFactory.CallList.get(1)).toEqual('lucterios.dummy->multi(personneMorale=\'100\',CONFIRME=\'YES\',bidule=\'aaa\',)')

    await currentUI.clickButton(0, 1)
    expect(!gui.isExist()).toEqual(true)
    expect(mObsFactory.CallList.size()).toEqual(2)
  })
})
