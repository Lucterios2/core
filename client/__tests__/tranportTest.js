'use strict'
/* global beforeEach, afterEach, describe, it, expect, jest */
import { HashMap, postLog, setServerUrl, LucteriosException } from '../src/utils.js'
import { HttpTransportImpl } from '../src/transport.js'
import axios from 'axios'
import Cookies from 'js-cookie'

jest.mock('axios')

var mTransport = null

setServerUrl(function () {
  return 'http://127.0.0.1:8000/'
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

    var newHttpTransport = new HttpTransportImpl()
    expect(newHttpTransport.getSession()).toBe('ABCDEF12345')
  })

  it('Image', () => {
    var newHttpTransport = new HttpTransportImpl()
    expect(newHttpTransport.getIconUrl('/static/lucterios.contacts/images/fields.png')).toBe('http://127.0.0.1:8000/static/lucterios.contacts/images/fields.png')
    expect(newHttpTransport.getIconUrl('static/lucterios.contacts/images/fields.png')).toBe('http://127.0.0.1:8000/static/lucterios.contacts/images/fields.png')
    expect(newHttpTransport.getIconUrl('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAABmJLR0QA')).toBe('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAABmJLR0QA')
  })

  it('Actions bad auth', async () => {
    var jsonMetaSended = { action: 'menu', observer: 'core.auth', title: 'info', extension: 'CORE' }
    var jsonRetour
    axios.get.mockClear()
    axios.delete.mockClear()
    axios.put.mockClear()
    axios.post.mockClear()
    axios.get.mockImplementation((url) => {
      return Promise.resolve({
        status: 200,
        data: {
          connexion: { INSTANCE: 'test' },
          meta: jsonMetaSended,
          data: 'NEEDAUTH',
          close: null,
          context: {}
        }
      })
    })

    postLog('cookie before:' + Cookies.get())
    jsonRetour = await mTransport.transfertFileFromServerString('CORE/menu', new HashMap())
    expect(jsonRetour.connexion.INSTANCE).toBe('test')
    delete jsonRetour.connexion
    expect(jsonRetour).toEqual({
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
    var jsonMetaSended = { action: 'legalEntityShow', observer: 'core.custom', title: 'Voir une personne morale', extension: 'lucterios.contacts' }
    var jsonRetour
    axios.get.mockClear()
    axios.delete.mockClear()
    axios.put.mockClear()
    axios.post.mockClear()
    axios.get.mockImplementation((url) => {
      return Promise.resolve({
        status: 200,
        data: {
          meta: jsonMetaSended,
          data: { img: '/static/lucterios.contacts/images/legalEntity.png', name: 'Les olympiens' },
          comp: [ { name: 'img' }, { name: 'name' } ],
          close: null,
          context: { legal_entity: 1 }
        }
      })
    })

    var params = new HashMap()
    params.put('legal_entity', 1)
    jsonRetour = await mTransport.transfertFileFromServerString('lucterios.contacts/legalEntityShow', params)
    expect(Object.keys(jsonRetour).length).toBe(5)
    expect(Object.keys(jsonRetour.data).length).toBe(2)
    expect(jsonRetour.comp.length).toBe(2)
    expect(jsonRetour.close).toBe(null)
    expect(jsonRetour.context).toEqual({ legal_entity: 1 })
    expect(jsonRetour.meta).toEqual({
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
    var jsonMetaSended = { action: 'authentification', observer: 'core.auth', title: 'info', extension: 'CORE' }
    var jsonRetour
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
          meta: jsonMetaSended,
          data: 'OK',
          close: null,
          context: { password: 'admin', username: 'admin', ses: 'admin' }
        }
      })
    })

    var params = new HashMap()
    params.put('username', 'admin')
    params.put('password', 'admin')
    jsonRetour = await mTransport.transfertFileFromServerString('CORE/authentification', params, 'POST')
    expect(Object.keys(jsonRetour).length).toBe(5)
    expect(jsonRetour.data).toBe('OK')
    expect(jsonRetour.close).toBe(null)
    expect(jsonRetour.context).toEqual({
      password: 'admin',
      username: 'admin',
      ses: 'admin'
    })
    expect(jsonRetour.meta).toEqual({
      action: 'authentification',
      observer: 'core.auth',
      title: 'info',
      extension: 'CORE'
    })
    mTransport.setSession(jsonRetour.context.session)
    expect(axios.get).toHaveBeenCalledTimes(0)
    expect(axios.put).toHaveBeenCalledTimes(0)
    expect(axios.post).toHaveBeenCalledTimes(1)
    expect(axios.delete).toHaveBeenCalledTimes(0)
    expect(lastPostReceiver[0]).toEqual('http://127.0.0.1:8000/CORE/authentification')
  })

  it('Actions delete', async () => {
    var jsonMetaSended = { action: 'usersDelete', observer: 'core.acknowledge', title: 'Suppression d\'utilisateurs', extension: 'CORE' }
    var jsonRetour
    axios.get.mockClear()
    axios.post.mockClear()
    axios.put.mockClear()
    axios.get.mockClear()
    axios.delete.mockImplementation((url) => {
      return Promise.resolve({
        status: 200,
        data: {
          meta: jsonMetaSended,
          close: null,
          context: { user_actif: 7 }
        }
      })
    })

    var params = new HashMap()
    params.put('user_actif', 7)
    params.put('CONFIRME', 'YES')
    jsonRetour = await mTransport.transfertFileFromServerString('CORE/usersDelete', params, 'DELETE')
    expect(Object.keys(jsonRetour).length).toBe(3)
    expect(jsonRetour.close).toBe(null)
    expect(jsonRetour.context).toEqual({ user_actif: 7 })
    expect(jsonRetour.meta).toEqual({
      action: 'usersDelete',
      observer: 'core.acknowledge',
      title: 'Suppression d\'utilisateurs',
      extension: 'CORE'
    })
    mTransport.setSession(jsonRetour.context.session)
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
      await mTransport.transfertFileFromServerString('foo', new HashMap(), 'HEADERS')
      expect(true).toBe(false)
    } catch (error) {
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
      return Promise.reject({ response: { status: 404, data: 'Not Implemented ' + url } }) // eslint-disable-line prefer-promise-reject-errors
    })
    try {
      await mTransport.transfertFileFromServerString('foo', new HashMap())
      expect(true).toBe(false)
    } catch (error) {
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
      return Promise.reject({ response: { status: 501, data: 'Bad ' + url } }) // eslint-disable-line prefer-promise-reject-errors
    })
    try {
      await mTransport.transfertFileFromServerString('foo', new HashMap())
      expect(true).toBe(false)
    } catch (error) {
      expect(error instanceof LucteriosException).toBe(true)
      expect(error.message).toEqual('Http error 501')
    }
    expect(axios.get).toHaveBeenCalledTimes(1)
    expect(axios.put).toHaveBeenCalledTimes(0)
    expect(axios.post).toHaveBeenCalledTimes(0)
    expect(axios.delete).toHaveBeenCalledTimes(0)
    expect(axios.get).toHaveBeenLastCalledWith('http://127.0.0.1:8000/foo')
  })
/*
  it('File', async () => {
    const Blob = require('node-blob')
    const atob = require('atob')
    axios.get.mockClear()
    axios.delete.mockClear()
    axios.put.mockClear()
    axios.get.mockClear()
    axios.post.mockImplementation((url) => {
      try {
        var newblob = new Blob(['1234567890'], { type: 'image/png' })
        newblob.name = 'add.png'
        return Promise.resolve(newblob)
      } catch (error) {
        return Promise.reject(new Error('BAD:' + error))
      }
    })

    Singleton().mFileManager.saveFile = function (aContent, aFileName) {
      expect(aFileName).toEqual('add.png')
      expect(atob(aContent)).toBe('1234567890')
    }
    await mTransport.getFileContent('static/lucterios.CORE/images/add.png', async function (blob) {
      await Singleton().mFileManager.saveBlob(blob, 'add.png')
    })
  })
*/
})
