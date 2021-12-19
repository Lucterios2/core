'use strict'
import { ObserverGUI } from './observer.js'
import { convertLuctoriosFormatToHtml, unusedVariables } from './utils.js'
import { CompBasic, GUIManage, createTable } from './gui.utils.js'

export class ObserverDialogBox extends ObserverGUI {
  getObserverName () {
    return 'core.dialogbox'
  }

  setContent (aJSON) {
    super.setContent(aJSON)
    var jsonText = this.mJSON.data
    this.mText = jsonText.text
    this.mType = parseInt(jsonText.type, 10) || 0
  }

  show (aTitle, aGUIType) {
    super.show(aTitle, aGUIType)
    var imageName = ''
    var table = []
    switch (this.mType) {
      case 2:
        imageName = 'images/confirm.png'
        break
      case 3:
        imageName = 'images/warning.png'
        break
      case 4:
        imageName = 'images/error.png'
        break
      default:
        imageName = 'images/info.png'
        break
    }
    this.mText = convertLuctoriosFormatToHtml(this.mText)
    table[0] = []
    table[0][0] = new CompBasic('<img src=\'' + imageName + '\' alt=\'' + imageName + '\'></img>')
    table[0][1] = new CompBasic('<label>' + this.mText + '</label>')

    this.mGUI = new GUIManage(this.getId(), this.mTitle, this)
    this.mGUI.addcontent(createTable(table), this.buildButtons())
    this.mGUI.showGUI(true)
  }

  getParameters (aCheckNull) {
    unusedVariables(aCheckNull)
    return this.mContext
  }
}

export var showMessageDialog = function (aText, aTitle, aType) {
  var obs = new ObserverDialogBox()
  if (aType === undefined) {
    obs.mType = 0
  } else {
    obs.mType = aType
  }
  obs.mText = aText
  obs.show(aTitle)
}
