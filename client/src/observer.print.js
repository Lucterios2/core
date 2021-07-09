'use strict'
import { ObserverAbstract } from './observer.js'
import { Singleton } from './singleton.js'
import { getFileNameWithoutForgottenChar } from './utils.js'

export var MODE_NONE = 0
export var MODE_PRINT = 1
export var MODE_PREVIEW = 2
export var MODE_EXPORT_PDF = 3
export var MODE_EXPORT_CSV = 4

export class ObserverPrint extends ObserverAbstract {
  constructor () {
    super()
    this.mode = MODE_NONE
    this.printContent = null
    this.title = ''
  }

  getObserverName () {
    return 'CORE.Print'
  }

  setContent (aJSON) {
    super.setContent(aJSON)
    this.printContent = null
    var printElements = this.mJSON.print
    this.title = printElements.title
    this.mode = parseInt(printElements.mode, 10) || MODE_PREVIEW
    if (printElements.extension === undefined) {
      if (this.mode === MODE_EXPORT_CSV) {
        this.extension = '.csv'
      } else {
        this.extension = '.pdf'
      }
    } else {
      this.extension = '.' + printElements.extension
    }
    this.printContent = printElements.content
  }

  show (aTitle, aGUIType) {
    super.show(aTitle, aGUIType)
    var fileName = getFileNameWithoutForgottenChar(this.title)
    fileName += this.extension
    Singleton().mFileManager.saveFile(this.printContent, fileName)
  }
}
