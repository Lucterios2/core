'use strict'
import { HashMap, postLog, setServerUrl, LucteriosException } from '../src/utils.js'
import { HttpTransportImpl } from '../src/transport.js'
import { Singleton } from '../src/singleton.js'
import axios from 'axios'
import Cookies from 'js-cookie'
const Blob = require('node-blob')
const atob = require('atob')

jest.mock('axios')

var mFileContent = null
var mFileName = null
var mTransport = null 

setServerUrl(function () {
  return "http://127.0.0.1:8000/"
})

beforeEach(() => {
  const cookieList = Cookies.get()
  Object.keys(cookieList).forEach((cookiesKey) => {
    Cookies.remove(cookiesKey)
  })
  mTransport = new HttpTransportImpl()
  mTransport.close()
})

afterEach(() => {
  mTransport.close()
  mTransport = null
  const cookieList = Cookies.get()
  Object.keys(cookieList).forEach((cookiesKey) => {
    Cookies.remove(cookiesKey)
  })
})

const saveFile = function (aContent, aFileName) {
  console.log('saveFile:'+aFileName)
  mFileContent = atob(aContent)
  mFileName = aFileName
}

const convertXML = function (data) {
  data = data.replace(/>\s*/g, '>'); // Replace '> ' with '>'
  data = data.replace(/\s*</g, '<'); // Replace '< ' with '<'
  var parser = new DOMParser()
  var xmlDoc = parser.parseFromString(data, 'text/xml')
  return (new XMLSerializer()).serializeToString(xmlDoc)
}

describe('TransportRest', () => {
  it('Connection', () => {
    expect(mTransport.getServerUrl()).toBe('http://127.0.0.1:8000/')
    expect(mTransport.getSession()).toBe('')

    mTransport.setSession('ABCDEF12345')
    expect(mTransport.getSession()).toBe('ABCDEF12345')

    expect(mTransport.getLastLogin()).toBe('')
    mTransport.setLastLogin('admin')
    expect(mTransport.getLastLogin()).toBe('admin')
  })

  it('Static', () => {
    expect(mTransport.getSession()).toBe('')
    mTransport.setSession('ABCDEF12345')
    expect(mTransport.getSession()).toBe('ABCDEF12345')

    var new_http_transport = new HttpTransportImpl()
    expect(new_http_transport.getSession()).toBe('ABCDEF12345')
  })

  it('Image', () => {
    var new_http_transport = new HttpTransportImpl()
    expect(new_http_transport.getIconUrl('/static/lucterios.contacts/images/fields.png')).toBe('http://127.0.0.1:8000/static/lucterios.contacts/images/fields.png')
    expect(new_http_transport.getIconUrl('static/lucterios.contacts/images/fields.png')).toBe('http://127.0.0.1:8000/static/lucterios.contacts/images/fields.png')
    expect(new_http_transport.getIconUrl('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAABmJLR0QA')).toBe('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAABmJLR0QA')
  })

  it('Actions bad auth', async () => {
	var json_meta_sended = { action: 'menu', observer: 'core.auth', title: 'info', extension: 'CORE' }   
    var json_retour
    axios.get.mockClear()
    axios.delete.mockClear()
    axios.put.mockClear()
    axios.post.mockClear()
    axios.get.mockImplementation((url) => {
    	return Promise.resolve({ 
    	  status: 200,
          data: { 
            connexion: { INSTANCE: 'test' }, 
            meta: json_meta_sended, 
            data: 'NEEDAUTH', 
            close: null, 
            context: {} 
          } 
    	})
    })
	  
    postLog('cookie before:' + Cookies.get())
    json_retour = await mTransport.transfertFileFromServerString('CORE/menu', new HashMap())
    expect(json_retour.connexion.INSTANCE).toBe('test')
    delete json_retour.connexion
    expect(json_retour).toEqual({
      data: 'NEEDAUTH',
      close: null,
      context: {},
      meta: {
        action: 'menu',
        observer: 'core.auth',
        title: 'info',
        extension: 'CORE'
      }
    })
    expect(axios.get).toHaveBeenCalledTimes(1)
    expect(axios.put).toHaveBeenCalledTimes(0)
    expect(axios.post).toHaveBeenCalledTimes(0)
    expect(axios.delete).toHaveBeenCalledTimes(0)
    expect(axios.get).toHaveBeenLastCalledWith('http://127.0.0.1:8000/CORE/menu')
    
  })

  it('Actions get', async () => {
	var json_meta_sended = { action: 'legalEntityShow', observer: 'core.custom', title: 'Voir une personne morale', extension: 'lucterios.contacts' }   
    var json_retour
    axios.get.mockClear()
    axios.delete.mockClear()
    axios.put.mockClear()
    axios.post.mockClear()
    axios.get.mockImplementation((url) => {
    	return Promise.resolve({ 
    	  status: 200,
          data: { 
            meta: json_meta_sended, 
            data: { img: '/static/lucterios.contacts/images/legalEntity.png', name: 'Les olympiens' },
            comp: [ { name: 'img' }, { name: 'name' }],
            close: null, 
            context: { legal_entity: 1 } 
          } 
    	})
    })
   
    var params = new HashMap()
	params.put('legal_entity', 1)
    json_retour = await mTransport.transfertFileFromServerString('lucterios.contacts/legalEntityShow', params)
    expect(Object.keys(json_retour).length).toBe(5)
    expect(Object.keys(json_retour.data).length).toBe(2)
    expect(json_retour.comp.length).toBe(2)
    expect(json_retour.close).toBe(null)
    expect(json_retour.context).toEqual({ legal_entity: 1 })
    expect(json_retour.meta).toEqual({
      action: 'legalEntityShow',
      observer: 'core.custom',
      title: 'Voir une personne morale',
      extension: 'lucterios.contacts'
    })
    expect(axios.get).toHaveBeenCalledTimes(1)
    expect(axios.put).toHaveBeenCalledTimes(0)
    expect(axios.post).toHaveBeenCalledTimes(0)
    expect(axios.delete).toHaveBeenCalledTimes(0)
    expect(axios.get).toHaveBeenLastCalledWith('http://127.0.0.1:8000/lucterios.contacts/legalEntityShow?legal_entity=1')
  })

  it('Actions post', async () => {
    var json_meta_sended = { action: 'authentification', observer: 'core.auth', title: 'info', extension: 'CORE' }   
    var json_retour
    var lastPostReceiver = null
    axios.get.mockClear()
    axios.delete.mockClear()
    axios.put.mockClear()
    axios.get.mockClear()
    axios.post.mockImplementation((url, params) => {
    	lastPostReceiver = [url, params]
        return Promise.resolve({ 
          status: 200,
          data: { 
            connexion: { INSTANCE: 'test' }, 
            meta: json_meta_sended, 
            data: 'OK', 
            close: null, 
            context: {password: 'admin', username: 'admin', ses: 'admin'} 
          } 
        })
    })
    
    var params = new HashMap()
    params.put('username', 'admin')
    params.put('password', 'admin')
    json_retour = await mTransport.transfertFileFromServerString('CORE/authentification', params ,'POST')
    expect(Object.keys(json_retour).length).toBe(5)
    expect(json_retour.data).toBe('OK')
    expect(json_retour.close).toBe(null)
    expect(json_retour.context).toEqual({
      password: 'admin',
      username: 'admin',
      ses: 'admin'
    })
    expect(json_retour.meta).toEqual({
      action: 'authentification',
      observer: 'core.auth',
      title: 'info',
      extension: 'CORE'
    })
    mTransport.setSession(json_retour.context.session)
    expect(axios.get).toHaveBeenCalledTimes(0)
    expect(axios.put).toHaveBeenCalledTimes(0)
    expect(axios.post).toHaveBeenCalledTimes(1)
    expect(axios.delete).toHaveBeenCalledTimes(0)
    expect(lastPostReceiver[0]).toEqual('http://127.0.0.1:8000/CORE/authentification')
  })

  it('Actions delete', async () => {
    var json_meta_sended = { action: 'usersDelete', observer: 'core.acknowledge', title: 'Suppression d\'utilisateurs', extension: 'CORE' }   
    var json_retour
    axios.get.mockClear()
    axios.post.mockClear()
    axios.put.mockClear()
    axios.get.mockClear()
    axios.delete.mockImplementation((url) => {
        return Promise.resolve({ 
          status: 200,
          data: { 
            meta: json_meta_sended, 
            close: null, 
            context: {user_actif: 7} 
          } 
        })
    })
    
    var params = new HashMap()
    params.put('user_actif', 7)
    params.put('CONFIRME', 'YES')
    json_retour = await mTransport.transfertFileFromServerString('CORE/usersDelete', params ,'DELETE')
    expect(Object.keys(json_retour).length).toBe(3)
    expect(json_retour.close).toBe(null)
    expect(json_retour.context).toEqual({
      user_actif: 7
    })
    expect(json_retour.meta).toEqual({
      action: 'usersDelete',
      observer: 'core.acknowledge',
      title: 'Suppression d\'utilisateurs',
      extension: 'CORE'
    })
    mTransport.setSession(json_retour.context.session)
    expect(axios.get).toHaveBeenCalledTimes(0)
    expect(axios.put).toHaveBeenCalledTimes(0)
    expect(axios.post).toHaveBeenCalledTimes(0)
    expect(axios.delete).toHaveBeenCalledTimes(1)
    expect(axios.delete).toHaveBeenLastCalledWith('http://127.0.0.1:8000/CORE/usersDelete?user_actif=7&CONFIRME=YES')
  })

  it('Actions bad method', async () => {
    axios.get.mockClear()
	axios.delete.mockClear()
	axios.put.mockClear()
	axios.get.mockClear()
    try {
	  await mTransport.transfertFileFromServerString('foo', new HashMap() ,'HEADERS')
	  expect(true).toBe(false)
	} catch(error) {
	  expect(error instanceof LucteriosException).toBe(true)
	  expect(error.message).toEqual('method unknown!')
	}
    expect(axios.get).toHaveBeenCalledTimes(0)
    expect(axios.put).toHaveBeenCalledTimes(0)
    expect(axios.post).toHaveBeenCalledTimes(0)
    expect(axios.delete).toHaveBeenCalledTimes(0)
  })
  
  it('Actions unknown command', async () => {
    axios.get.mockClear()
	axios.delete.mockClear()
	axios.put.mockClear()
	axios.get.mockClear()
    axios.get.mockImplementation((url) => {
      return Promise.reject({ response: { status: 404, data: 'Not Implemented ' + url } })
    })
	try {
	  await mTransport.transfertFileFromServerString('foo', new HashMap())
	  expect(true).toBe(false)
	} catch(error) {
	  expect(error instanceof LucteriosException).toBe(true)
	  expect(error.message).toEqual('Command unknown!')
	}
	expect(axios.get).toHaveBeenCalledTimes(1)
	expect(axios.put).toHaveBeenCalledTimes(0)
	expect(axios.post).toHaveBeenCalledTimes(0)
	expect(axios.delete).toHaveBeenCalledTimes(0)
	expect(axios.get).toHaveBeenLastCalledWith('http://127.0.0.1:8000/foo')
  })

  it('Actions unknown command', async () => {
    axios.get.mockClear()
	axios.delete.mockClear()
	axios.put.mockClear()
	axios.get.mockClear()
    axios.get.mockImplementation((url) => {
      return Promise.reject({ response: { status: 501, data: 'Bad ' + url } })
    })
	try {
	  await mTransport.transfertFileFromServerString('foo', new HashMap())
	  expect(true).toBe(false)
	} catch(error) {
	  expect(error instanceof LucteriosException).toBe(true)
	  expect(error.message).toEqual('Http error 501')
	}
	expect(axios.get).toHaveBeenCalledTimes(1)
	expect(axios.put).toHaveBeenCalledTimes(0)
	expect(axios.post).toHaveBeenCalledTimes(0)
	expect(axios.delete).toHaveBeenCalledTimes(0)
	expect(axios.get).toHaveBeenLastCalledWith('http://127.0.0.1:8000/foo')
  })
  
  it('File', async () => {
    axios.get.mockClear()
    axios.delete.mockClear()
    axios.put.mockClear()
    axios.get.mockClear()
    axios.post.mockImplementation((url) => {
	  try {
	    var newblob = new Blob(['1234567890'], { type: 'image/png' })
	    newblob.name = 'add.png'
	    return Promise.resolve(newblob)
	   } catch(error) {
	    return Promise.reject('BAD:' + error) 
	   }
    })
	 
    expect(mFileContent).toBe(null)
    Singleton().mFileManager.saveFile = function (aContent, aFileName) {
      expect(aFileName).toEqual( 'add.png')
	  expect(atob(aContent)).toBe('1234567890')
    }
    await mTransport.getFileContent('static/lucterios.CORE/images/add.png', async function(blob) {
      await Singleton().mFileManager.saveBlob(blob, 'add.png')
    })
  })
 
})
