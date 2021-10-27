'use strict'
/* global beforeEach, afterEach, describe, it, expect */
import { HttpTransportStub, ObserverFactoryMock, ObserverAcknowledgeNoParent, UIMock } from './mock.js'
import { Singleton, SingletonClose } from '../src/singleton.js'
import { ObserverCustom } from '../src/observer.custom.js'
import { ActionImpl, FORM_MODAL } from '../src/action.js'
import { formatToString } from '../src/gui.utils.js'
const html = require('fs').readFileSync('./index.html').toString()
const $ = require('jquery')
const currentUI = new UIMock()
const Blob = require('node-blob')

var mObsFactory = null

beforeEach(() => {
  document.documentElement.innerHTML = html
  mObsFactory = new ObserverFactoryMock()
  Singleton().setHttpTransportClass(HttpTransportStub)
  Singleton().setFactory(mObsFactory)
  Singleton().setActionClass(ActionImpl)
  Singleton().Transport().setSession('abc123')
  Singleton().mSelectLang = 'fr'
  ObserverFactoryMock.NewObserver = new ObserverAcknowledgeNoParent()
})

afterEach(() => {
  SingletonClose()
})

describe('ObserverCustom', () => {
  it('Custom_Simple', function () {
    var jsonReceive = {
      'actions': [],
      'context': {},
      'close': null,
      'data': {
        'dummytitle': 'Dummy',
        'dummy_time': '2017-10-26T19:42:12.033'
      },
      'meta': {
        'action': 'statusMenu',
        'title': 'R\u00e9sum\u00e9',
        'extension': 'CORE',
        'observer': 'core.custom'
      },
      'comp': [ {
        'description': '',
        'y': 0,
        'needed': false,
        'x': 0,
        'component': 'LABELFORM',
        'rowspan': 1,
        'name': 'dummytitle',
        'tab': 0,
        'colspan': 4,
        'formatstr': '{[center]}{[u]}{[b]}{0}{[/b]}{[/u]}{[/center]}',
        'formatnum': null
      }, {
        'description': '',
        'y': 1,
        'needed': false,
        'x': 0,
        'component': 'LABELFORM',
        'rowspan': 1,
        'name': 'dummy_time',
        'tab': 0,
        'colspan': 4,
        'formatstr': '{[center]}{[font color=\'blue\']}{0}{[/font]}{[/center]}',
        'formatnum': 'H'
      } ]
    }
    currentUI.clean()

    var obs = new ObserverCustom()
    obs.setSource('CORE', 'statusMenu')
    obs.setContent(jsonReceive)
    obs.show('Résumé', FORM_MODAL)

    var gui = obs.getGUI()
    expect(gui != null).toEqual(true)
    expect(gui.isExist()).toEqual(true)
    var jcnt = gui.getHtmlDom()

    var lbl = jcnt.find('table:eq(0) > tbody > tr:eq(0) > td:eq(0) > lct-cell > span')
    expect(lbl.html()).toEqual('<center><u><b>Dummy</b></u></center>')

    lbl = jcnt.find('table:eq(0) > tbody > tr:eq(1) > td:eq(0) > lct-cell > span')
    var datetimeVal = lbl.html()
    expect(datetimeVal.substring(0, 48)).toEqual('<center><font color="blue">jeudi 26 octobre 2017')
    expect(datetimeVal.substring(datetimeVal.length - 21)).toEqual('19:42</font></center>')

    expect($.fn.dialog).toHaveBeenCalledTimes(1)
    expect(currentUI.optionsDialog.length).toBe(1)
    expect(currentUI.buttonCount(0)).toEqual(1)
    expect(currentUI.getTextButton(0, 0)).toEqual('Fermer')

    obs.close()
    expect(!gui.isExist()).toEqual(true)
    expect(mObsFactory.CallList.size()).toEqual(0)
  })

  it('Custom_EditMemo', async () => {
    var jsonReceive = {
      'context': {
        'LOCK_IDENT': 'lucterios.contacts.models-LegalEntity-1'
      },
      'comp': [ {
        'y': 0,
        'rowspan': 6,
        'colspan': 1,
        'type': '',
        'component': 'IMAGE',
        'name': 'img',
        'needed': false,
        'description': '',
        'tab': 0,
        'x': 0
      }, {
        'action': null,
        'colspan': 2,
        'is_default': false,
        'rowspan': 1,
        'description': 'nom',
        'tab': 0,
        'size': 100,
        'is_mini': false,
        'y': 0,
        'name': 'name',
        'reg_expr': '',
        'component': 'EDIT',
        'javascript': '',
        'needed': true,
        'x': 1
      }, {
        'action': null,
        'submenu': [],
        'colspan': 2,
        'is_default': false,
        'rowspan': 1,
        'description': 'adresse',
        'tab': 0,
        'x': 1,
        'y': 2,
        'name': 'address',
        'HMin': 200,
        'component': 'MEMO',
        'javascript': '',
        'needed': true,
        'is_mini': false,
        'with_hypertext': false,
        'VMin': 50
      }, {
        'action': {
          'id': 'postal_code',
          'action': 'currentStructureAddModify',
          'extension': 'lucterios.contacts',
          'text': '',
          'modal': '2',
          'params': null,
          'close': '0',
          'icon': '/static/lucterios.contacts/images/ourDetails.png',
          'unique': '1',
          'name': 'postal_code'
        },
        'colspan': 1,
        'is_default': false,
        'rowspan': 1,
        'description': 'code postal',
        'tab': 0,
        'size': 10,
        'is_mini': false,
        'y': 3,
        'name': 'postal_code',
        'reg_expr': '',
        'component': 'EDIT',
        'javascript': '',
        'needed': true,
        'x': 1
      }, {
        'action': null,
        'colspan': 1,
        'is_default': false,
        'rowspan': 1,
        'description': 'ville',
        'tab': 0,
        'size': 100,
        'is_mini': false,
        'y': 3,
        'name': 'city',
        'reg_expr': '',
        'component': 'EDIT',
        'javascript': '',
        'needed': true,
        'x': 2
      }, {
        'action': null,
        'colspan': 2,
        'is_default': false,
        'rowspan': 1,
        'description': 'pays',
        'tab': 0,
        'size': 100,
        'is_mini': false,
        'y': 4,
        'name': 'country',
        'reg_expr': '',
        'component': 'EDIT',
        'javascript': '',
        'needed': false,
        'x': 1
      }, {
        'action': null,
        'colspan': 1,
        'is_default': false,
        'rowspan': 1,
        'description': 'tel1',
        'tab': 0,
        'size': 20,
        'is_mini': false,
        'y': 5,
        'name': 'tel1',
        'reg_expr': '',
        'component': 'EDIT',
        'javascript': '',
        'needed': false,
        'x': 1
      }, {
        'action': null,
        'colspan': 1,
        'is_default': false,
        'rowspan': 1,
        'description': 'tel2',
        'tab': 0,
        'size': 20,
        'is_mini': false,
        'y': 5,
        'name': 'tel2',
        'reg_expr': '',
        'component': 'EDIT',
        'javascript': '',
        'needed': false,
        'x': 2
      }, {
        'action': null,
        'colspan': 2,
        'is_default': false,
        'rowspan': 1,
        'description': 'courriel',
        'tab': 0,
        'size': 254,
        'is_mini': false,
        'y': 6,
        'name': 'email',
        'reg_expr': '',
        'component': 'EDIT',
        'javascript': '',
        'needed': false,
        'x': 1
      }, {
        'action': null,
        'submenu': [],
        'colspan': 2,
        'is_default': false,
        'rowspan': 1,
        'description': 'commentaire',
        'tab': 0,
        'x': 1,
        'y': 7,
        'name': 'comment',
        'HMin': 200,
        'component': 'MEMO',
        'javascript': '',
        'needed': false,
        'is_mini': false,
        'with_hypertext': false,
        'VMin': 50
      }, {
        'action': null,
        'submenu': [],
        'colspan': 2,
        'is_default': false,
        'rowspan': 1,
        'description': 'N\u00b0 SIRET/SIREN',
        'tab': 0,
        'x': 1,
        'y': 8,
        'name': 'identify_number',
        'HMin': 200,
        'component': 'MEMO',
        'javascript': '',
        'needed': false,
        'is_mini': false,
        'with_hypertext': false,
        'VMin': 50
      }, {
        'action': null,
        'colspan': 1,
        'is_default': false,
        'rowspan': 1,
        'description': 'text',
        'tab': 0,
        'size': -1,
        'is_mini': false,
        'y': 13,
        'name': 'custom_1',
        'reg_expr': '',
        'component': 'EDIT',
        'javascript': '',
        'needed': false,
        'x': 1
      }, {
        'action': null,
        'min': 1.0,
        'colspan': 2,
        'is_default': false,
        'rowspan': 1,
        'description': 'numero',
        'tab': 0,
        'prec': 0,
        'is_mini': false,
        'y': 13,
        'name': 'custom_2',
        'component': 'FLOAT',
        'javascript': '',
        'needed': true,
        'max': 100.0,
        'x': 2
      }, {
        'action': null,
        'colspan': 1,
        'case': [ [ 0, 'bb' ], [ 1, 'dd' ], [ 2, 'aa' ], [ 3, 'cc' ] ],
        'is_default': false,
        'rowspan': 1,
        'description': 'choix',
        'tab': 0,
        'is_mini': false,
        'y': 14,
        'name': 'custom_4',
        'component': 'SELECT',
        'javascript': '',
        'needed': false,
        'x': 1
      }, {
        'action': null,
        'colspan': 2,
        'is_default': false,
        'rowspan': 1,
        'description': 'Sur?',
        'tab': 0,
        'is_mini': false,
        'y': 14,
        'name': 'custom_5',
        'component': 'CHECK',
        'javascript': '',
        'needed': false,
        'x': 2
      }, {
        'action': null,
        'colspan': 2,
        'is_default': false,
        'rowspan': 1,
        'description': 'Captcha',
        'tab': 0,
        'is_mini': false,
        'y': 15,
        'name': 'captcha',
        'component': 'CAPTCHA',
        'javascript': '',
        'needed': false,
        'x': 1
      } ],
      'close': {
        'id': 'CORE/unlock',
        'action': 'unlock',
        'text': 'unlock',
        'modal': '1',
        'params': null,
        'close': '1',
        'extension': 'CORE',
        'unique': '1'
      },
      'meta': {
        'action': 'currentStructureAddModify',
        'title': 'Nos coordonn\u00e9es',
        'extension': 'lucterios.contacts',
        'observer': 'core.custom'
      },
      'data': {
        'tel2': '',
        'comment': '',
        'img': '/static/lucterios.contacts/images/ourDetails.png',
        'name': 'Association Multi\'sport de d\u00e9monstration',
        'email': 'info@sd-libre.fr',
        'custom_5': 0,
        'tel1': '0987654321',
        'address': 'place central',
        'identify_number': '',
        'custom_1': '',
        'custom_2': 0,
        'city': 'TRIFOUILLY',
        'uploadlogo': '',
        'postal_code': '99000',
        'country': '',
        'custom_4': 0
      },
      'actions': [ {
        'id': 'lucterios.contacts/currentStructureAddModify',
        'action': 'currentStructureAddModify',
        'extension': 'lucterios.contacts',
        'text': 'Ok',
        'modal': '1',
        'params': {
          'SAVE': 'YES'
        },
        'close': '1',
        'icon': '/static/lucterios.CORE/images/ok.png',
        'unique': '1'
      }, {
        'id': '',
        'modal': '1',
        'text': 'Annuler',
        'params': null,
        'close': '1',
        'icon': '/static/lucterios.CORE/images/cancel.png',
        'unique': '1'
      } ]
    }
    currentUI.clean()
    var obs = new ObserverCustom()
    obs.setSource('lucterios.contacts', 'currentStructureAddModify')
    obs.setContent(jsonReceive)
    obs.show('Nos coordonnées', FORM_MODAL)

    var gui = obs.getGUI()
    expect(gui != null).toEqual(true)
    expect(gui.isExist()).toEqual(true)
    var jcnt = gui.getHtmlDom()

    var comp = jcnt.find('table:eq(0) > tbody > tr:eq(0) > td:eq(0) > lct-cell > img')
    var img = comp.attr('src')
    expect(img.substring(0, img.indexOf('='))).toEqual('STUB//static/lucterios.contacts/images/ourDetails.png?val')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(0) > td:eq(1) > lct-cell > label')
    expect(comp.html()).toEqual('nom')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(0) > td:eq(1) > lct-cell > lct-ctrl > input')
    expect(comp.val()).toEqual('Association Multi\'sport de démonstration')
    comp.focus()
    comp.val('AAA')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(2) > td:eq(0) > lct-cell > label')
    expect(comp.html()).toEqual('adresse')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(2) > td:eq(0) > lct-cell > lct-ctrl > textarea')
    expect(comp.text()).toEqual('place central')
    comp.focus()
    comp.text('BBB\nCCC')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(3) > td:eq(0) > lct-cell > label')
    expect(comp.html()).toEqual('code postal')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(3) > td:eq(0) > lct-cell > lct-ctrl > input')
    expect(comp.val()).toEqual('99000')
    comp.focus()
    comp.val('123456')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(3) > td:eq(1) > lct-cell > label')
    expect(comp.html()).toEqual('ville')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(3) > td:eq(1) > lct-cell > lct-ctrl > input')
    expect(comp.val()).toEqual('TRIFOUILLY')
    comp.focus()
    comp.val('DDDD')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(4) > td:eq(0) > lct-cell > label')
    expect(comp.html()).toEqual('pays')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(4) > td:eq(0) > lct-cell > lct-ctrl > input')
    expect(comp.val()).toEqual('')
    comp.focus()
    comp.val('EEEE')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(5) > td:eq(0) > lct-cell > label')
    expect(comp.html()).toEqual('tel1')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(5) > td:eq(0) > lct-cell > lct-ctrl > input')
    expect(comp.val()).toEqual('0987654321')
    comp.focus()
    comp.val('FFFFF')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(5) > td:eq(1) > lct-cell > label')
    expect(comp.html()).toEqual('tel2')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(5) > td:eq(1) > lct-cell > lct-ctrl > input')
    expect(comp.val()).toEqual('')
    comp.focus()
    comp.val('GGGGG')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(6) > td:eq(1) > lct-cell > label')
    expect(comp.html()).toEqual('courriel')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(6) > td:eq(1) > lct-cell > lct-ctrl > input')
    expect(comp.val()).toEqual('info@sd-libre.fr')
    comp.focus()
    comp.val('IIIII')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(7) > td:eq(1) > lct-cell > label')
    expect(comp.html()).toEqual('commentaire')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(7) > td:eq(1) > lct-cell > lct-ctrl > textarea')
    expect(comp.text()).toEqual('')
    comp.focus()
    comp.text('LL\nMMMM\nNN')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(8) > td:eq(1) > lct-cell > label')
    expect(comp.html()).toEqual('N° SIRET/SIREN')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(8) > td:eq(1) > lct-cell > lct-ctrl > textarea')
    expect(comp.text()).toEqual('')
    comp.focus()
    comp.text('JJ\nKKKK')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(11) > td:eq(1) > lct-cell > label')
    expect(comp.html()).toEqual('Captcha')
    comp = jcnt.find('table:eq(0) > tbody > tr:eq(11) > td:eq(1) > lct-cell > lct-ctrl')
    var captchInfo = comp.text().split(' ')
    var captchValue = 0
    if (captchInfo[1] === '-') {
      captchValue = parseInt(captchInfo[0]) - parseInt(captchInfo[4])
    }
    if (captchInfo[1] === '+') {
      captchValue = parseInt(captchInfo[4]) - parseInt(captchInfo[0])
    }
    if (captchInfo[1] === 'x') {
      captchValue = parseInt(captchInfo[4]) / parseInt(captchInfo[0])
    }
    comp = jcnt.find('table:eq(0) > tbody > tr:eq(11) > td:eq(1) > lct-cell > lct-ctrl > input')
    comp.val(captchValue.toString())

    expect($.fn.dialog).toHaveBeenCalledTimes(1)
    expect(currentUI.optionsDialog.length).toBe(1)
    expect(currentUI.buttonCount(0)).toEqual(2)
    expect(currentUI.getTextButton(0, 0)).toEqual('Ok')
    expect(currentUI.getTextButton(0, 1)).toEqual('Annuler')

    mObsFactory.init()

    expect(mObsFactory.CallList.size()).toEqual(0)
    await currentUI.clickButton(0, 0)

    expect(!gui.isExist()).toEqual(true)
    expect(mObsFactory.CallList.size()).toEqual(2)
    var expectedCmd = 'CORE->unlock(LOCK_IDENT=\'lucterios.contacts.models-LegalEntity-1\',)'
    expect(mObsFactory.CallList.get(0)).toEqual(expectedCmd)
    expectedCmd = 'lucterios.contacts->currentStructureAddModify(LOCK_IDENT=\'lucterios.contacts.models-LegalEntity-1\',name=\'AAA\',address=\'BBB{[br/]}CCC\',postal_code=\'123456\',city=\'DDDD\',country=\'EEEE\',tel1=\'FFFFF\',tel2=\'GGGGG\',email=\'IIIII\',comment=\'LL{[br/]}MMMM{[br/]}NN\',identify_number=\'JJ{[br/]}KKKK\',custom_1=\'\',custom_2=\'1\',custom_4=\'0\',custom_5=\'n\',captcha=\'' + captchValue.toString() + '\',SAVE=\'YES\',)'
    expect(mObsFactory.CallList.get(1)).toEqual(expectedCmd)
  })

  it('Custom_Upload', async () => {
    var jsonReceive = {
      'meta': {
        'action': 'documentAddModify',
        'title': 'Ajouter un document',
        'observer': 'core.custom',
        'extension': 'lucterios.documents'
      },
      'actions': [ {
        'text': 'Ok',
        'params': {
          'SAVE': 'YES'
        },
        'icon': '/static/lucterios.CORE/images/ok.png',
        'modal': '1',
        'unique': '1',
        'id': 'lucterios.documents/documentAddModify',
        'action': 'documentAddModify',
        'close': '1',
        'extension': 'lucterios.documents'
      }, {
        'text': 'Annuler',
        'icon': '/static/lucterios.CORE/images/cancel.png',
        'modal': '1',
        'unique': '1',
        'id': '',
        'params': null,
        'close': '1'
      } ],
      'comp': [ {
        'tab': 0,
        'needed': false,
        'filter': [ '.jpg', '.png', '.gif' ],
        'maxsize': 16777216,
        'component': 'UPLOAD',
        'description': '',
        'x': 1,
        'compress': false,
        'rowspan': 1,
        'y': 1,
        'name': 'filename',
        'colspan': 1,
        'http_file': true
      }, {
        'HMin': 200,
        'tab': 0,
        'needed': true,
        'VMin': 50,
        'component': 'MEMO',
        'description': 'description',
        'javascript': '',
        'is_mini': false,
        'is_default': false,
        'submenu': [],
        'x': 1,
        'action': null,
        'rowspan': 1,
        'with_hypertext': false,
        'y': 2,
        'name': 'description',
        'colspan': 1
      } ],
      'data': {
        'description': '',
        'filename': ''
      },
      'context': {},
      'close': null
    }
    var contentFile = 'This file is part of Diacamma, a software developped by \'Le Sanglier du Libre\' (http://www.sd-libre.fr)\n' +
       'Thanks to have payed a retribution for using this module.\n' +
       '\n' +
       'Diacamma is free software; you can redistribute it and/or modify\n' +
       'it under the terms of the GNU General Public License as published by\n' +
       'the Free Software Foundation; either version 2 of the License, or\n' +
       '(at your option) any later version.\n' +
       '\n' +
       'Diacamma is distributed in the hope that it will be useful,\n' +
       'but WITHOUT ANY WARRANTY; without even the implied warranty of\n' +
       'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n' +
       'GNU General Public License for more details.\n' +
       '\n' +
       'You should have received a copy of the GNU General Public License\n' +
       'along with Lucterios; if not, write to the Free Software\n' +
       'Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA'
    currentUI.clean()

    var obs = new ObserverCustom()
    obs.setSource('lucterios.documents', 'documentAddModify')
    obs.setContent(jsonReceive)
    obs.show('Ajouter un document', FORM_MODAL)

    obs.mCompList.get('filename').getValue = function () {
      var blobContent = new Blob([ contentFile ], {
        type: 'text/plain;charset=UTF-8'
      })
      blobContent.name = 'undefined'
      return blobContent
    }

    var gui = obs.getGUI()
    expect(gui != null).toEqual(true)
    expect(gui.isExist()).toEqual(true)
    var jcnt = gui.getHtmlDom()

    var comp = jcnt.find('table:eq(0) > tbody > tr:eq(0) > td:eq(1) > lct-cell > div > input')
    expect(comp.attr('accept')).toEqual('.jpg,.png,.gif')
    await comp.change()

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(1) > td:eq(1) > lct-cell > label')
    expect(comp.html()).toEqual('description')

    comp = jcnt.find('table:eq(0) > tbody > tr:eq(1) > td:eq(1) > lct-cell > lct-ctrl > textarea')
    expect(comp.text()).toEqual('')
    comp.focus()
    comp.text('JJ\nKKKK')

    expect($.fn.dialog).toHaveBeenCalledTimes(1)
    expect(currentUI.optionsDialog.length).toBe(1)
    expect(currentUI.buttonCount(0)).toEqual(2)
    expect(currentUI.getTextButton(0, 0)).toEqual('Ok')
    expect(currentUI.getTextButton(0, 1)).toEqual('Annuler')

    expect(mObsFactory.CallList.size()).toEqual(0)

    var currentFactory = mObsFactory
    await currentUI.clickButton(0, 0)
    expect(!gui.isExist()).toEqual(true)
    expect(currentFactory.CallList.size()).toEqual(1)
    var expectedCmd = 'lucterios.documents->documentAddModify(description=\'JJ{[br/]}KKKK\',SAVE=\'YES\',)'
    expect(currentFactory.CallList.get(0)).toEqual(expectedCmd)
  })

  it('Custom_Download', async () => {
    var jsonReceive = {
      'meta': {
        'action': 'documentShow',
        'title': 'Afficher le document',
        'observer': 'core.custom',
        'extension': 'lucterios.documents'
      },
      'actions': [ {
        'text': 'Modifier',
        'params': null,
        'icon': '/static/lucterios.CORE/images/edit.png',
        'modal': '1',
        'unique': '1',
        'id': 'lucterios.documents/documentAddModify',
        'action': 'documentAddModify',
        'close': '1',
        'extension': 'lucterios.documents'
      }, {
        'text': 'Fermer',
        'icon': '/static/lucterios.CORE/images/close.png',
        'modal': '1',
        'unique': '1',
        'id': '',
        'params': null,
        'close': '1'
      } ],
      'comp': [ {
        'x': 1,
        'description': 'nom',
        'needed': false,
        'tab': 0,
        'rowspan': 1,
        'component': 'LABELFORM',
        'y': 1,
        'name': 'name',
        'colspan': 2,
        'formatstr': '{0}{0}',
        'formatnum': null
      }, {
        'tab': 0,
        'maxsize': 0,
        'needed': false,
        'filename': 'CORE/download?filename=documents/document_1&sign=4ac745f17656cfc30c3586b87d50e50a',
        'component': 'DOWNLOAD',
        'description': '',
        'javascript': '',
        'is_mini': false,
        'is_default': false,
        'x': 1,
        'compress': false,
        'action': {
          'text': 'Ajouter',
          'params': null,
          'icon': '/static/lucterios.CORE/images/add.png',
          'modal': '1',
          'unique': '1',
          'id': 'filename',
          'action': 'documentAddModify',
          'name': 'filename',
          'close': '0',
          'extension': 'lucterios.documents'
        },
        'rowspan': 1,
        'y': 2,
        'name': 'filename',
        'colspan': 4,
        'http_file': true
      } ],
      'data': {
        'filename': 'modelstatus.doc',
        'name': 'modelstatus.doc'
      },
      'context': {
        'LOCK_IDENT': 'lucterios.documents.models-Document-1',
        'document': '1'
      },
      'close': {
        'text': 'unlock',
        'params': null,
        'modal': '1',
        'unique': '1',
        'id': 'CORE/unlock',
        'action': 'unlock',
        'close': '1',
        'extension': 'CORE'
      }
    }
    var contentFile = 'This file is part of Diacamma, a software developped by \'Le Sanglier du Libre\' (http://www.sd-libre.fr)\n' +
    'Thanks to have payed a retribution for using this module.\n' +
    '\n' +
    'Diacamma is free software; you can redistribute it and/or modify\n' +
    'it under the terms of the GNU General Public License as published by\n' +
    'the Free Software Foundation; either version 2 of the License, or\n' +
    '(at your option) any later version.\n' +
    '\n' +
    'Diacamma is distributed in the hope that it will be useful,\n' +
    'but WITHOUT ANY WARRANTY; without even the implied warranty of\n' +
    'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n' +
    'GNU General Public License for more details.\n' +
    '\n' +
    'You should have received a copy of the GNU General Public License\n' +
    'along with Lucterios; if not, write to the Free Software\n' +
    'Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA'
    currentUI.clean()
    var fileContent = null
    var fileName = null

    Singleton().Transport().JSONReceive = contentFile
    Singleton().mFileManager.saveBlob = function (aBlob, aFileName) {
      fileContent = aBlob
      fileName = aFileName
    }
    expect(fileContent).toEqual(null)

    var obs = new ObserverCustom()
    obs.setSource('lucterios.documents', 'documentShow')
    obs.setContent(jsonReceive)
    obs.show('Afficher le document', FORM_MODAL)

    var gui = obs.getGUI()
    expect(gui != null).toEqual(true)
    expect(gui.isExist()).toEqual(true)
    var jcnt = gui.getHtmlDom()

    var compLbl = jcnt.find('table:eq(0) > tbody > tr:eq(1) > td:eq(1) > lct-cell > label')
    expect(compLbl.html()).toEqual('modelstatus.doc')
    var compDownload = jcnt.find('table:eq(0) > tbody > tr:eq(1) > td:eq(1) > lct-cell > button')
    expect(compDownload.text()).toEqual('Enregistrer sous...')

    expect($.fn.dialog).toHaveBeenCalledTimes(1)
    expect(currentUI.optionsDialog.length).toBe(1)
    expect(currentUI.buttonCount(0)).toEqual(2)
    expect(currentUI.getTextButton(0, 0)).toEqual('Modifier')
    expect(currentUI.getTextButton(0, 1)).toEqual('Fermer')

    expect(mObsFactory.CallList.size()).toEqual(0)

    await compDownload.click()

    expect(fileName).toEqual('modelstatus.doc')
    expect(fileContent != null).toEqual(true)
    expect(fileContent.size).toEqual(contentFile.length)
    expect(Singleton().Transport().XmlParam['URL']).toEqual('CORE/download?filename=documents/document_1&sign=4ac745f17656cfc30c3586b87d50e50a')
    expect(mObsFactory.CallList.size()).toEqual(0)
    await currentUI.clickButton(0, 1)
    expect(mObsFactory.CallList.size()).toEqual(1)
    expect(mObsFactory.CallList.get(0)).toEqual('CORE->unlock(LOCK_IDENT=\'lucterios.documents.models-Document-1\',document=\'1\',)')
  })

  it('Custom_Grid', async () => {
    var jsonReceive = {
      'meta': {
        'action': 'postalCodeList',
        'title': 'Code postal',
        'observer': 'core.custom',
        'extension': 'lucterios.contacts'
      },
      'actions': [
        {
          'text': 'Fermer',
          'icon': '/static/lucterios.CORE/images/close.png',
          'modal': '1',
          'unique': '1',
          'id': '',
          'params': null,
          'close': '1'
        }
      ],
      'comp': [
        {
          'x': 0,
          'description': '',
          'needed': false,
          'tab': 0,
          'rowspan': 1,
          'component': 'IMAGE',
          'y': 0,
          'name': 'img',
          'colspan': 1,
          'type': ''
        },
        {
          'x': 1,
          'description': '',
          'needed': false,
          'tab': 0,
          'rowspan': 1,
          'component': 'LABELFORM',
          'y': 0,
          'name': 'filtre',
          'colspan': 1,
          'formatstr': '{0}',
          'formatnum': null
        },
        {
          'tab': 0,
          'needed': false,
          'component': 'EDIT',
          'description': '',
          'javascript': '',
          'is_mini': false,
          'size': -1,
          'is_default': false,
          'x': 1,
          'reg_expr': '',
          'action': {
            'text': 'Code postal',
            'params': null,
            'icon': '/static/lucterios.contacts/images/postalCode.png',
            'modal': '2',
            'unique': '1',
            'id': 'filter_postal_code',
            'action': 'postalCodeList',
            'name': 'filter_postal_code',
            'close': '0',
            'extension': 'lucterios.contacts'
          },
          'rowspan': 1,
          'y': 1,
          'name': 'filter_postal_code',
          'colspan': 1
        },
        {
          'HMin': 500,
          'tab': 0,
          'needed': false,
          'headers': [ [ 'postal_code', 'code postal', 'N0', 1, '{0}' ], [ 'city', 'ville', null, 1, '{0}' ], [ 'country', 'pays', null, 1, '{[b]}{0}{[/b]}' ] ],
          'VMin': 200,
          'component': 'GRID',
          'description': '',
          'page_max': 1,
          'x': 0,
          'order': null,
          'actions': [ {
            'text': 'Ajouter',
            'params': null,
            'icon': '/static/lucterios.CORE/images/add.png',
            'modal': '1',
            'unique': '0',
            'id': 'lucterios.contacts/postalCodeAdd',
            'action': 'postalCodeAdd',
            'close': '0',
            'extension': 'lucterios.contacts'
          } ],
          'rowspan': 1,
          'y': 2,
          'name': 'postalCode',
          'colspan': 2,
          'page_num': 0
        }, {
          'x': 0,
          'description': '',
          'needed': false,
          'tab': 0,
          'rowspan': 1,
          'component': 'LABELFORM',
          'y': 3,
          'name': 'nb_postalCode',
          'colspan': 2
        }
      ],
      'data': {
        'nb_postalCode': 'Nombre total de codes postaux: 5',
        'img': '/static/lucterios.contacts/images/postalCode.png',
        'filter_postal_code': '3842',
        'postalCode': [ {
          'city': 'DOMENE',
          'country': 'France',
          'postal_code': 38420,
          'id': 13052
        }, {
          'city': 'LE VERSOUD',
          'country': 'France',
          'postal_code': 38420,
          'id': 19686
        }, {
          'city': 'MURIANETTE',
          'country': 'France',
          'postal_code': 38420,
          'id': 41059
        }, {
          'city': 'REVEL',
          'country': 'France',
          'postal_code': 38420,
          'id': 26703
        }, {
          'city': 'ST JEAN LE VIEUX',
          'country': 'France',
          'postal_code': 38420,
          'id': 30019
        } ],
        'filtre': '{[b]}Filtrer par code postal{[/b]}'
      },
      'context': {
        'filter_postal_code': '3842'
      },
      'close': null
    }
    currentUI.clean()

    var obs = new ObserverCustom()
    obs.setSource('lucterios.contacts', 'postalCodeList')
    obs.setContent(jsonReceive)
    obs.show('Code postal', FORM_MODAL)

    var gui = obs.getGUI()
    expect(gui != null).toEqual(true)
    expect(gui.isExist()).toEqual(true)
    var jcnt = gui.getHtmlDom()

    var tableComp = jcnt.find('table:eq(0) > tbody > tr:eq(2) > td:eq(0) > lct-cell')
    var tableHeader = tableComp.find('div.gridContent > table > thead > tr:eq(0)')
    var tableContent = tableComp.find('div.gridContent > table > tbody')
    var tableButtons = tableComp.find('div.gridActions')

    var comp = tableHeader.find('th:eq(0)')
    expect(comp.text().trim()).toEqual('code postal')
    comp = tableHeader.find('th:eq(1)')
    expect(comp.text().trim()).toEqual('ville')
    comp = tableHeader.find('th:eq(2)')
    expect(comp.text().trim()).toEqual('pays')

    var cell1 = tableContent.find('tr:eq(0) > td:eq(0)')
    expect(cell1.text()).toEqual('38 420')
    var cell2 = tableContent.find('tr:eq(1) > td:eq(1)')
    expect(cell2.text()).toEqual('LE VERSOUD')
    var cell3 = tableContent.find('tr:eq(2) > td:eq(2)')
    expect(cell3.html()).toEqual('<b>France</b>')

    var btn1 = tableButtons.find('button:eq(0)')
    expect(btn1.text()).toEqual('Ajouter')
    expect(btn1.prop('disabled')).toEqual(true)

    var row2 = tableContent.find('tr:eq(1)')
    expect(row2.hasClass('selected')).toEqual(false)
    await row2.click()

    expect(row2.hasClass('selected')).toEqual(true)
    expect(btn1.prop('disabled')).toEqual(false)

    expect(mObsFactory.CallList.size()).toEqual(0)

    await btn1.click()
    expect(mObsFactory.CallList.size()).toEqual(1)
    expect(mObsFactory.CallList.get(0)).toEqual('lucterios.contacts->postalCodeAdd(filter_postal_code=\'3842\',postalCode=\'19686\',)')

    gui.close()
    expect(!gui.isExist()).toEqual(true)
  })

  it('test_formating_general', () => {
    Singleton().mSelectLang = 'fr'

    expect(formatToString(null, null, null)).toEqual('---')
    expect(formatToString('abc', null, null)).toEqual('abc')
    expect(formatToString('abc', null, '{0}')).toEqual('abc')
    expect(formatToString([ 'abc', 'uvw', 'xyz' ], null, null)).toEqual('abc{[br/]}uvw{[br/]}xyz')
    expect(formatToString('abc', null, '{[i]}{[b]}{0}{[/b]}{[/i]}')).toEqual('{[i]}{[b]}abc{[/b]}{[/i]}')
    expect(formatToString([ 'abc', 'uvw', 'xyz' ], null, '{0}: {1} --> {2}')).toEqual('abc: uvw --> xyz')
    expect(formatToString([ 65.4, 456.04, 894730.124 ], 'N2', '{0}: {1} --> {2}')).toEqual('65,40: 456,04 --> 894 730,12')
    expect(formatToString({
      'value': 'abc',
      'format': '{[b]}{0}{[/b]}'
    }, null, '{[i]}{0}{[/i]}')).toEqual('{[i]}{[b]}abc{[/b]}{[/i]}')

    expect(formatToString(1234.56, null, '{[i]}{0}{[/i]};{[b]}{0}{[/b]}')).toEqual('{[i]}1234.56{[/i]}')
    expect(formatToString(-1234.56, null, '{[i]}{0}{[/i]};{[b]}{0}{[/b]}')).toEqual('{[b]}1234.56{[/b]}')

    expect(formatToString(0.000001, 'C2EUR', '{0};A')).toEqual('A')
    expect(formatToString(-0.000001, 'C2EUR', '{0};A')).toEqual('A')
    expect(formatToString(-0.000001, 'C2EUR', '{0};A;B')).toEqual('B')
    expect(formatToString(0.000001, 'C2EUR', '{0};A;B')).toEqual('B')

    expect(formatToString(0, {
      '0': 'aaa',
      '1': 'bbb',
      '2': 'ccc'
    }, '{0}')).toEqual('aaa')
    expect(formatToString(1, {
      '0': 'aaa',
      '1': 'bbb',
      '2': 'ccc'
    }, '{0}')).toEqual('bbb')
    expect(formatToString(2, {
      '0': 'aaa',
      '1': 'bbb',
      '2': 'ccc'
    }, '{0}')).toEqual('ccc')
    expect(formatToString(3, {
      '0': 'aaa',
      '1': 'bbb',
      '2': 'ccc'
    }, '{0}')).toEqual('3')
  })

  it('test_formating_fr', () => {
    Singleton().mSelectLang = 'fr'

    expect(formatToString(1234.56, 'N3', '{[i]}{0}{[/i]};{[b]}{0}{[/b]}')).toEqual('{[i]}1 234,560{[/i]}')
    expect(formatToString(-1234.56, 'N3', '{[i]}{0}{[/i]};{[b]}{0}{[/b]}')).toEqual('{[b]}1 234,560{[/b]}')
    expect(formatToString(1234.56, 'N0', '{0}')).toEqual('1 235')

    expect(formatToString(1234.56, 'N3', '{0}')).toEqual('1 234,560')
    expect(formatToString(-1234.56, 'N3', '{0}')).toEqual('-1 234,560')
    expect(formatToString(1234.56, 'C2EUR', '{0}')).toEqual('1 234,56 €')
    expect(formatToString(-1234.56, 'C2EUR', '{0}')).toEqual('-1 234,56 €')

    expect(formatToString(1234.56, 'C2EUR', '{0};')).toEqual('1 234,56 €')
    expect(formatToString(1234.56, 'C2EUR', 'Crédit {0};Débit {0}')).toEqual('Crédit 1 234,56 €')
    expect(formatToString(1234.56, 'C2EUR', '{[font color=\'green\']}Crédit {0}{[/font]};{[font color=\'blue\']}Débit {0}{[/font]}')).toEqual('{[font color=\'green\']}Crédit 1 234,56 €{[/font]}')
    expect(formatToString(1234.56, 'N2', '{0}')).toEqual('1 234,56')
    expect(formatToString(1234.56, 'C2EUR', '{0};{0}')).toEqual('1 234,56 €')
    expect(formatToString(1234.56, 'C2EUR', '{0}')).toEqual('1 234,56 €')
    expect(formatToString(1234.56, 'C2EUR', '{[font color=\'green\']}{0}{[/font]};{[font color=\'blue\']}{0}{[/font]}')).toEqual('{[font color=\'green\']}1 234,56 €{[/font]}')

    expect(formatToString(-1234.56, 'C2EUR', '{0};')).toEqual('-1 234,56 €')
    expect(formatToString(-1234.56, 'C2EUR', 'Crédit {0};Débit {0}')).toEqual('Débit 1 234,56 €')
    expect(formatToString(-1234.56, 'C2EUR', '{[font color=\'green\']}Crédit {0}{[/font]};{[font color=\'blue\']}Débit {0}{[/font]}')).toEqual('{[font color=\'blue\']}Débit 1 234,56 €{[/font]}')
    expect(formatToString(-1234.56, 'N2', '{0}')).toEqual('-1 234,56')
    expect(formatToString(-1234.56, 'C2EUR', '{0};{0}')).toEqual('1 234,56 €')
    expect(formatToString(-1234.56, 'C2EUR', '{0}')).toEqual('-1 234,56 €')
    expect(formatToString(-1234.56, 'C2EUR', '{[font color=\'green\']}{0}{[/font]};{[font color=\'blue\']}{0}{[/font]}')).toEqual('{[font color=\'blue\']}1 234,56 €{[/font]}')

    expect(formatToString('2017-04-23', 'D', '{0}')).toEqual('23 avril 2017')
    expect(formatToString('12:54:25.014', 'T', '{0}')).toEqual('12:54')
    expect(formatToString('2017-04-23T12:54:25.014', 'H', '{0}').substring(0, 22)).toEqual('dimanche 23 avril 2017')
    var value = formatToString('2017-04-23T12:54:25.014', 'H', '{0}')
    expect(value.substring(value.length - 5)).toEqual('12:54')

    expect(formatToString(true, 'B', '{0}')).toEqual('Oui')
    expect(formatToString(false, 'B', '{0}')).toEqual('Non')
  })

  it('test_formating_en', () => {
    Singleton().mSelectLang = 'en'

    expect(formatToString(1234.56, 'N3', '{[i]}{0}{[/i]};{[b]}{0}{[/b]}')).toEqual('{[i]}1,234.560{[/i]}')
    expect(formatToString(-1234.56, 'N3', '{[i]}{0}{[/i]};{[b]}{0}{[/b]}')).toEqual('{[b]}1,234.560{[/b]}')
    expect(formatToString(1234.56, 'N0', '{0}')).toEqual('1,235')

    expect(formatToString(1234.56, 'N3', '{0}')).toEqual('1,234.560')
    expect(formatToString(-1234.56, 'N3', '{0}')).toEqual('-1,234.560')
    expect(formatToString(1234.56, 'C2USD', '{0}')).toEqual('$1,234.56')
    expect(formatToString(-1234.56, 'C2USD', '{0}')).toEqual('-$1,234.56')

    expect(formatToString('2017-04-23', 'D', '{0}')).toEqual('April 23, 2017')
    expect(formatToString('12:54:25.014', 'T', '{0}')).toEqual('12:54 PM')
    expect(formatToString('2017-04-23T12:54:25.014', 'H', '{0}')).toEqual('Sunday, April 23, 2017, 12:54 PM')

    expect(formatToString(true, 'B', '{0}')).toEqual('Yes')
    expect(formatToString(false, 'B', '{0}')).toEqual('No')
  })
})
