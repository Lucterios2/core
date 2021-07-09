'use strict'
import { HttpTransportStub, ObserverFactoryMock, ObserverAcknowledgeNoParent, UIMock } from './mock.js'
import { Singleton, SingletonClose } from '../src/singleton.js'
import { ObserverMenu } from '../src/observer.menu.js'
import { ActionImpl } from '../src/action.js'
const html = require('fs').readFileSync('./index.html').toString()
const $ = require('jquery')
const currentUI = new UIMock()

var mFileContent = null
var mObsFactory = null

beforeEach(() => {
  document.documentElement.innerHTML = html
  mObsFactory = new ObserverFactoryMock()
  Singleton().setHttpTransportClass(HttpTransportStub)
  Singleton().setFactory(mObsFactory)
  Singleton().setActionClass(ActionImpl)
  Singleton().Transport().setSession('abc123')
  ObserverFactoryMock.NewObserver = new ObserverAcknowledgeNoParent()
})

afterEach(() => {
  SingletonClose()
})

describe('ObserverMenu',  () => {
  it('Menu_Simple', () => {
    var json_receive = {
      'meta': {
        observer : 'core.menu',
        source_extension : 'CORE',
        source_action : 'menu',
        text : 'Menu de l application'
      },
      'context': {},
      'menus': [ {
        'icon': '/static/lucterios.CORE/images/general.png',
        'help': 'G\u00e9n\u00e9ralit\u00e9',
        'id': 'core.general',
        'menus': [ {
          'params': null,
          'icon': '/static/lucterios.CORE/images/passwd.png',
          'help': 'Pour changer de mot de passe.',
          'id': 'CORE/changePassword',
          'unique': '1',
          'modal': '1',
          'text': 'Mot de passe',
          'action': 'changePassword',
          'extension': 'CORE',
          'close': '1'
        } ],
        'unique': '1',
        'modal': '1',
        'text': 'G\u00e9n\u00e9ral',
        'params': null,
        'close': '1'
      }, {
        'icon': '/static/lucterios.CORE/images/admin.png',
        'help': 'Gestion des r\u00e9glages et des configurations',
        'id': 'core.admin',
        'menus': [ {
          'params': null,
          'icon': '/static/lucterios.CORE/images/config.png',
          'help': 'Afficher et modifier les param\u00e8tres principaux.',
          'id': 'CORE/configuration',
          'unique': '1',
          'modal': '1',
          'text': 'Configuration g\u00e9n\u00e9rale',
          'action': 'configuration',
          'extension': 'CORE',
          'close': '1'
        }, {
          'icon': '/static/lucterios.CORE/images/config_ext.png',
          'help': 'G\u00e9rer les configurations des modules',
          'id': 'core.extensions',
          'menus': [ {
            'params': null,
            'icon': '/static/lucterios.CORE/images/config_search.png',
            'help': 'Liste de crit\u00e8res sauvegard\u00e9s pour les outils de recherche',
            'id': 'CORE/savedCriteriaList',
            'unique': '1',
            'modal': '0',
            'text': 'Crit\u00e8res sauvegard\u00e9s',
            'action': 'savedCriteriaList',
            'extension': 'CORE',
            'close': '1'
          } ],
          'unique': '1',
          'modal': '1',
          'text': 'Modules (conf.)',
          'params': null,
          'close': '1'
        }, {
          'icon': '/static/lucterios.CORE/images/permissions.png',
          'help': 'G\u00e9rer les utilisateurs, groupes et permissions.',
          'id': 'core.right',
          'menus': [ {
            'params': null,
            'icon': '/static/lucterios.CORE/images/group.png',
            'help': 'G\u00e9rer les groupes.',
            'id': 'CORE/groupsList',
            'unique': '1',
            'modal': '0',
            'text': 'Les groupes',
            'action': 'groupsList',
            'extension': 'CORE',
            'close': '1'
          }, {
            'params': null,
            'icon': '/static/lucterios.CORE/images/user.png',
            'help': 'G\u00e9rer les utilisateurs.',
            'id': 'CORE/usersList',
            'unique': '1',
            'modal': '0',
            'text': 'Utilisateurs',
            'action': 'usersList',
            'extension': 'CORE',
            'close': '1'
          }, {
            'params': null,
            'icon': '/static/lucterios.CORE/images/session.png',
            'help': 'G\u00e9rer les sessions.',
            'id': 'CORE/sessionList',
            'unique': '1',
            'modal': '0',
            'text': 'Sessions',
            'action': 'sessionList',
            'extension': 'CORE',
            'close': '1'
          } ],
          'unique': '1',
          'modal': '1',
          'text': 'Gestion des droits',
          'params': null,
          'close': '1'
        } ],
        'unique': '1',
        'modal': '1',
        'text': 'Administration',
        'params': null,
        'close': '1'
      } ]
    }
    currentUI.clean()
    var obs = new ObserverMenu()
    obs.setSource('CORE', 'menu')
    obs.setContent(json_receive)
    obs.show('')

    expect(obs.menu_list.length).toEqual(2)
    expect(obs.menu_list[0].level).toEqual(0)
    expect(obs.menu_list[0].icon).toEqual('/static/lucterios.CORE/images/general.png')
    expect(obs.menu_list[0].extension).toEqual('')
    expect(obs.menu_list[0].action).toEqual('')
    expect(obs.menu_list[0].modal).toEqual(1)
    expect(obs.menu_list[0].help).toEqual('Généralité')
    expect(obs.menu_list[0].txt).toEqual('Général')
    expect(obs.menu_list[0].submenu.length).toEqual(1)

    var gui = obs.getGUI()
    expect(gui == null).toEqual(true)

    var jcnt = $('#menuContainer')

    var lbl = jcnt.find('div:eq(0) > ul:eq(0) > li:eq(0) > a:eq(0) > span:eq(0)')
    expect(lbl.text()).toEqual('Général')
    var lbl = jcnt.find('div:eq(0) > ul:eq(0) > li:eq(1) > a:eq(0) > span:eq(0)')
    expect(lbl.text()).toEqual('Administration')

    var btn1 = jcnt.find('div:eq(0) > div:eq(0) > button:eq(0)')
    expect(btn1.text()).toEqual('Mot de passePour changer de mot de passe.')

    var btn2 = jcnt.find('div:eq(0) > div:eq(1) > button:eq(1)')
    expect(btn2.text()).toEqual('Critères sauvegardésListe de critères sauvegardés pour les outils de recherche')

    expect(mObsFactory.CallList.size()).toEqual(0)

    btn1.click()
    expect(mObsFactory.CallList.size()).toEqual(1)
    var expected_cmd = 'CORE->changePassword()'
    expect(mObsFactory.CallList.get(0)).toEqual(expected_cmd)

    btn2.click()
    expect(mObsFactory.CallList.size()).toEqual(2)
    var expected_cmd = 'CORE->savedCriteriaList()'
    expect(mObsFactory.CallList.get(1)).toEqual(expected_cmd)

    obs.close()
  })

  it('Menu_Status', () => {
    var json_receive = {
      meta : {
        observer : 'core.menu',
        source_extension : 'CORE',
        source_action : 'menu',
        text : 'Menu de l application'
      },
      'context': {},
      menus : [ {
        'id': 'core.menu',
        'menus': [ {
          'params': null,
          'icon': '/static/lucterios.CORE/images/status.png',
          'help': 'R\u00e9sum\u00e9',
          'id': 'CORE/statusMenu',
          'unique': '1',
          'modal': '1',
          'text': 'R\u00e9sum\u00e9',
          'action': 'statusMenu',
          'extension': 'CORE',
          'close': '1'
        } ],
        'unique': '1',
        'modal': '1',
        'text': '',
        'params': null,
        'close': '1'
      }, {
        'icon': '/static/lucterios.CORE/images/general.png',
        'help': 'G\u00e9n\u00e9ralit\u00e9',
        'id': 'core.general',
        'menus': [ {
          'params': null,
          'icon': '/static/lucterios.CORE/images/passwd.png',
          'help': 'Pour changer de mot de passe.',
          'id': 'CORE/changePassword',
          'unique': '1',
          'modal': '1',
          'text': 'Mot de passe',
          'action': 'changePassword',
          'extension': 'CORE',
          'close': '1'
        } ],
        'unique': '1',
        'modal': '1',
        'text': 'G\u00e9n\u00e9ral',
        'params': null,
        'close': '1'
      } ]
    }
    currentUI.clean()

    var obs = new ObserverMenu()
    obs.setSource('CORE', 'menu')
    obs.setContent(json_receive)
    obs.show('')

    var gui = obs.getGUI()
    expect(gui == null).toEqual(true)

    var jcnt = $('#menuContainer')

    obs.close()
  })
})
