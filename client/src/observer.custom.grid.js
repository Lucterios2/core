'use strict'
import { LucteriosException, MINOR, convertLuctoriosFormatToHtml } from './utils.js'
import { Singleton } from './singleton.js'
import { SELECT_NONE, SELECT_SINGLE, SELECT_MULTI } from './action.js'
import { formatToString } from './gui.utils.js'
import { CompGeneric, CompButton } from './observer.custom.comp.js'
const $ = require('jquery')
const util = require('util')

class CompGridHeader {
  constructor () {
    this.name = ''
    this.type = ''
    this.orderable = 0
    this.label = ''
    this.formatstr = '%s'
    this.grid = null
  }

  initial (headcomp, grid) {
    this.name = headcomp[0]
    this.label = headcomp[1]
    this.type = headcomp[2]
    this.orderable = headcomp[3]
    this.formatstr = (headcomp[4] || '%s')
    this.grid = grid
  }

  getId () {
    return util.format('grid-%sHead-%s', this.grid.name, this.name.replace('.', '__'))
  }

  getHtml () {
    var headclass = ''
    var sortVal
    var sort = ''
    if (this.orderable === 1) {
      headclass = ' classHeader'
      sortVal = this.grid.getColumnOrder(this.name.replace('.', '__'))
      if (sortVal > 0) {
        sort = '<span class="ui-icon ui-icon-triangle-1-n">&nbsp;</span>'
      }
      if (sortVal < 0) {
        sort = '<span class="ui-icon ui-icon-triangle-1-s">&nbsp;</span>'
      }
    }
    return util.format('<th id="%s" class="%s">%s%s</th>', this.getId(), headclass, this.label, sort)
  }

  addAction () {
    if (this.orderable === 1) {
      var currentComp = $('#' + this.getId())
      currentComp.click($.proxy(function () {
        this.grid.orderColumn(this.name.replace('.', '__'))
      }, this))
    }
  }
}

class CompGridValue {
  constructor () {
    this.name = ''
    this.value = ''
    this.parentGrid = ''
  }

  initial (name, value) {
    this.name = name
    this.value = value
  }

  setParentGrid (grid) {
    this.parentGrid = grid
  }

  getHtml () {
    var cellType
    var label
    if (this.value === '') {
      return '<td></td>'
    }
    cellType = this.parentGrid.getValueType(this.name)
    if (cellType === 'icon') {
      return util.format('<td><img src="%s"></td>', Singleton().Transport().getIconUrl(this.value))
    }

    label = formatToString(this.value, cellType, this.parentGrid.getFormatStr(this.name))
    return util.format('<td>%s</td>', convertLuctoriosFormatToHtml(label))
  }
}

class CompGridRow {
  constructor () {
    this.id = 0
    this.values = null
    this.grid = ''
    this.rowIdx = 0
    this.colorIdx = 0
  }

  initial (rowIdx, rowcomp, grid, colorIdx) {
    this.rowIdx = rowIdx
    this.colorIdx = colorIdx
    this.grid = grid
    this.id = rowcomp.id

    var iCol
    var colName
    var val
    this.values = []
    for (iCol = 0; iCol < this.grid.gridHeaders.length; iCol++) {
      colName = this.grid.gridHeaders[iCol].name
      val = new CompGridValue()
      val.initial(colName, rowcomp[colName])
      val.setParentGrid(this.grid)
      this.values[this.values.length] = val
    }
  }

  getHtml () {
    var html
    var idxVal
    html = util.format('<tr id="%s_%s" pq-row-indx="%s" class="%s">', this.grid.name, this.id, this.rowIdx, (this.colorIdx % 2) === 0 ? 'odd' : '')
    for (idxVal = 0; idxVal < this.values.length; idxVal++) {
      html += this.values[idxVal].getHtml()
    }
    html += '</tr>'
    return html
  }

  selectGridRow (event) {
    this.grid.changeSelectRow(this.rowIdx, !this.isSelected(), event.shiftKey)
  }

  dbClickRow () {
    this.grid.clearSelectRow(true)
    var row = $(util.format('#%s_%s', this.grid.name, this.id))
    row.addClass('selected')
    this.grid.dbclick()
  }

  setSelected (select) {
    var row = $(util.format('#%s_%s', this.grid.name, this.id))
    if (select) {
      row.addClass('selected')
    } else {
      row.removeClass('selected')
    }
  }

  isSelected () {
    var row = $(util.format('#%s_%s', this.grid.name, this.id))
    return row.hasClass('selected')
  }

  addAction () {
    var row = $(util.format('#%s_%s', this.grid.name, this.id))
    row.click($.proxy(this.selectGridRow, this))
    row.dblclick($.proxy(this.dbClickRow, this))
  }
}

export class CompGrid extends CompGeneric {
  constructor (aOwner) {
    super(aOwner)
    this.args = {}
    this.buttons = null
    this.hasMulti = false
    this.hasSelect = false
    this.pageMax = 1
    this.pageNum = 0
    this.sizeByPage = 25
    this.nbLines = 0
    this.gridHeaders = null
    this.grid_Rows = null
    this.sortIndx = []
    this.sortDir = []
    this.lastRowSelected = -1
  }

  initial (component) {
    super.initial(component)
    this.tag = 'div'
    this.pageMax = parseInt(component['page_max'], 10) || 1
    this.pageNum = parseInt(component['page_num'], 10) || 0
    this.size_byPage = parseInt(component['size_by_page'], 10) || 25
    this.nbLines = parseInt(component['nb_lines'], 10) || 0
    this.noPager = component['no_pager'] || false
    this.selectedList = []

    this._orderManage(component)
    this._headerManage(component)
    this._rowsManage(component)
    this._actionManage(component)
  }

  _orderManage (component) {
    var iChild
    this.order = component.order || []
    this.sortIndx = []
    this.sortDir = []
    for (iChild = 0; iChild < this.order.length; iChild++) {
      if (this.order[iChild].substring(0, 1) === '-') {
        this.sortIndx.push(this.order[iChild].substring(1))
        this.sortDir.push('down')
      } else {
        this.sortIndx.push(this.order[iChild])
        this.sortDir.push('up')
      }
    }
  }

  _headerManage (component) {
    var heads = component.headers
    var iChild
    var header
    this.gridHeaders = []
    for (iChild = 0; iChild < heads.length; iChild++) {
      header = new CompGridHeader()
      header.initial(heads[iChild], this)
      this.gridHeaders[this.gridHeaders.length] = header
    }
  }

  getValueType (name) {
    var iCol
    for (iCol = 0; iCol < this.gridHeaders.length; iCol++) {
      if (this.gridHeaders[iCol].name === name) {
        return this.gridHeaders[iCol].type
      }
    }
    // ne devrait jamais arriver mais par defaut, on retourne null
    return null
  }

  getFormatStr (name) {
    var iCol
    for (iCol = 0; iCol < this.gridHeaders.length; iCol++) {
      if (this.gridHeaders[iCol].name === name) {
        return this.gridHeaders[iCol].formatstr
      }
    }
    return '%s'
  }

  _rowsManage (component) {
    var iChild
    var row
    var colorIdx = 0
    this.grid_Rows = []
    for (iChild = 0; iChild < component.value.length; iChild++) {
      if (iChild > 0) {
        if ((component.value[iChild].__colorRef__ === null) || (component.value[iChild].__colorRef__ !== component.value[iChild - 1].__colorRef__)) {
          colorIdx++
        }
      }
      row = new CompGridRow()
      row.initial(iChild, component.value[iChild], this, colorIdx)
      this.grid_Rows[this.grid_Rows.length] = row
    }
  }

  _actionManage (component) {
    var iChild
    var btn
    this.buttons = []
    if (component.actions) {
      for (iChild = 0; iChild < component.actions.length; iChild++) {
        btn = new CompButton(this.owner)
        btn.initial(component.actions[iChild])
        btn.name = util.format('%s_%s', this.name, iChild)
        btn.notifyPerformed = $.proxy(this._saveScroll, this)
        btn.description = ''
        btn.action = Singleton().CreateAction()
        btn.action.initialize(this.owner, Singleton().Factory(), component.actions[iChild])
        if (btn.action.mSelect === SELECT_MULTI) {
          this.hasMulti = true
        }
        if (btn.action.mSelect !== SELECT_NONE) {
          this.hasSelect = true
        }
        btn.isMini = (btn.action.getTitle() === '')
        this.buttons[this.buttons.length] = btn
      }
    }
  }

  getValue () {
    var selectedList = this.getSelectedId()
    return selectedList.join(';')
  }

  initialVal () {
    return ''
  }

  setValue (jsonvalue) {
    this.initial(jsonvalue)
    this.getGUIComp().html(this.getSubHtml())
  }

  getPagerHtml () {
    var rppindex
    var rPPOptions = [ 25, 50, 100, 250, 500 ]
    var html = ''
    var attribdisabled = 'ui-button-disabled ui-state-disabled" disabled=""'
    if (!this.noPager) {
      html = '<div class="gridpager" id="' + this.name + '_pager">'
      html += util.format('<button type="button" title="%s" class="ui-button ui-corner-all ui-widget ui-button-icon-only %s style="margin-left: 10px;"><span class="ui-button-icon ui-icon ui-icon-seek-first"></span><span class="ui-button-icon-space"></span></button>', Singleton().getTranslate('FirstPage'), this.pageNum === 0 ? attribdisabled : '"')
      html += util.format('<button type="button" title="%s" class="ui-button ui-corner-all ui-widget ui-button-icon-only %s><span class="ui-button-icon ui-icon ui-icon-seek-prev"></span><span class="ui-button-icon-space"></span></button>', Singleton().getTranslate('PrevPage'), this.pageNum === 0 ? attribdisabled : '"')
      html += '<span class="gridseparator"></span>'
      html += util.format('<span>Page</span><input tabindex="0" class="ui-corner-all" type="text" value="%s"><span>/</span><span class="total">%s</span></span>', this.pageNum + 1, this.pageMax)
      html += '<span class="gridseparator"></span>'
      html += util.format('<button type="button" title="%s" class="ui-button ui-corner-all ui-widget ui-button-icon-only %s"><span class="ui-button-icon ui-icon ui-icon-seek-next"></span><span class="ui-button-icon-space"> </span></button>', Singleton().getTranslate('NextPage'), (this.pageNum + 1) === this.pageMax ? attribdisabled : '"')
      html += util.format('<button type="button" title="%s" class="ui-button ui-corner-all ui-widget ui-button-icon-only %s"><span class="ui-button-icon ui-icon ui-icon-seek-end"></span><span class="ui-button-icon-space"> </span></button>', Singleton().getTranslate('LastPage'), (this.pageNum + 1) === this.pageMax ? attribdisabled : '"')
      html += '<span class="gridseparator"></span>'
      html += util.format(util.format('<span>%s</span><select class="ui-corner-all">', Singleton().getTranslate('Rpp')), '')
      for (rppindex = 0; rppindex < rPPOptions.length; rppindex++) {
        html += util.format('<option value="%s" %s>%s</option>', rPPOptions[rppindex], rPPOptions[rppindex] === this.size_byPage ? 'selected' : '', rPPOptions[rppindex])
      }
      html += '</select></span>'
      html += '<span class="gridseparator"></span>'
      if (this.nbLines > 0) {
        html += util.format(util.format('<span class="pq-pager-msg">%s</span>', Singleton().getTranslate('Display')), this.pageNum * this.size_byPage + 1, Math.min((this.pageNum + 1) * this.size_byPage, this.nbLines), this.nbLines)
      } else {
        html += '<span class="pq-pager-msg"></span>'
      }
      html += '</div>'
    }
    return html
  }

  getSubHtml () {
    var iBtn
    var iRow
    var iHead
    var html = ''
    var style = ''
    html = util.format('<div name="%s" %s>', this.name, style)
    if (this.buttons.length > 0) {
      html += '<div class="gridActions" id="' + this.name + '_actions">'
      for (iBtn = 0; iBtn < this.buttons.length; iBtn++) {
        html += this.buttons[iBtn].getSubHtml()
      }
      html += '</div>'
    }
    html += this.getPagerHtml()
    html += util.format('<div class="gridContent %s">', !this.noPager ? 'gridscroll' : '')
    html += '<table cellspacing="0" cellpadding="0"><thead><tr>'
    for (iHead = 0; iHead < this.gridHeaders.length; iHead++) {
      html += this.gridHeaders[iHead].getHtml()
    }
    html += '</tr></thead><tbody>'
    if (this.grid_Rows.length === 0) {
      html += util.format('<tr class="gridempty"><td colspan="%s">%s</td></tr>', this.gridHeaders.length, Singleton().getTranslate('NoRows'))
    } else {
      for (iRow = 0; iRow < this.grid_Rows.length; iRow++) {
        html += this.grid_Rows[iRow].getHtml()
      }
    }
    html += '</tbody></table></div>'
    html += '</div>'
    return html
  }

  addAction () {
    var iCol
    var iRow
    var iBtn
    var pqPager
    for (iCol = 0; iCol < this.gridHeaders.length; iCol++) {
      this.gridHeaders[iCol].addAction()
    }
    for (iRow = 0; iRow < this.grid_Rows.length; iRow++) {
      this.grid_Rows[iRow].addAction()
    }
    for (iBtn = 0; iBtn < this.buttons.length; iBtn++) {
      this.buttons[iBtn].addAction()
      this.buttons[iBtn].setSelectType(SELECT_NONE)
    }
    pqPager = $('#' + this.owner.getId()).find(util.format('div[id="%s_pager"]:eq(0)', this.name))
    pqPager.find('span.ui-icon-seek-first').parent().click($.proxy(function () {
      this.changeNumpage(0)
    }, this))
    pqPager.find('span.ui-icon-seek-prev').parent().click($.proxy(function () {
      this.changeNumpage(this.pageNum - 1)
    }, this))
    pqPager.find('span.ui-icon-seek-next').parent().click($.proxy(function () {
      this.changeNumpage(this.pageNum + 1)
    }, this))
    pqPager.find('span.ui-icon-seek-end').parent().click($.proxy(function () {
      this.changeNumpage(this.pageMax - 1)
    }, this))
    pqPager.find('input').change($.proxy(function (event) {
      this.changeNumpage(parseInt(event.currentTarget.value, 10) - 1)
    }, this))
    pqPager.find('select').change($.proxy(function (event) {
      this.changeSizepage(event.currentTarget.value)
    }, this))
    this._loadScroll()
  }

  _loadScroll () {
    var divScroll
    var scrollPos = $('#' + this.owner.getId()).prop(util.format('scroll_%s', this.name))
    if (scrollPos !== undefined) {
      divScroll = $('#' + this.owner.getId()).find('div.gridContent:eq(0)')
      divScroll[0].scrollTop = scrollPos
    }
  }

  _saveScroll () {
    var divScroll = $('#' + this.owner.getId()).find('div.gridContent:eq(0)')
    $('#' + this.owner.getId()).prop(util.format('scroll_%s', this.name), divScroll[0].scrollTop)
  }

  guiFinalize () {
  }

  clearSelectRow (allclear) {
    if (!this.hasMulti || allclear) {
      var iRow
      for (iRow = 0; iRow < this.grid_Rows.length; iRow++) {
        this.grid_Rows[iRow].setSelected(false)
      }
    }
  }

  getSelectedId () {
    var selectedList = []
    var iRow
    for (iRow = 0; iRow < this.grid_Rows.length; iRow++) {
      if (this.grid_Rows[iRow].isSelected()) {
        selectedList.push(this.grid_Rows[iRow].id)
      }
    }
    return selectedList
  }

  changeSelectRow (rowidx, newSelectVal, withRange) {
    if (!this.hasSelect) {
      return
    }
    if (newSelectVal) {
      this.clearSelectRow(false)
    }
    if (withRange && (this.lastRowSelected !== -1) && (this.lastRowSelected !== rowidx)) {
      var rowIdx
      var minRow = Math.min(this.lastRowSelected + 1, rowidx)
      var maxRow = Math.max(this.lastRowSelected - 1, rowidx)
      for (rowIdx = minRow; rowIdx <= maxRow; rowIdx++) {
        this.grid_Rows[rowIdx].setSelected(newSelectVal)
      }
    } else {
      this.grid_Rows[rowidx].setSelected(newSelectVal)
    }
    this.lastRowSelected = rowidx
    this.selectChange()
  }

  selectChange () {
    var selectedList = this.getSelectedId()
    var selectType
    var iBtn
    if (selectedList.length === 0) {
      selectType = SELECT_NONE
    } else if (selectedList.length === 1) {
      selectType = SELECT_SINGLE
    } else {
      selectType = SELECT_MULTI
    }
    for (iBtn = 0; iBtn < this.buttons.length; iBtn++) {
      this.buttons[iBtn].setSelectType(selectType)
    }
  }

  changeNumpage (newPage) {
    this.owner.getContext().put(util.format('GRID_PAGE%%%s', this.name), newPage)
    this.owner.getContext().put(util.format('GRID_SIZE%%%s', this.name), this.size_byPage)
    this.owner.refresh()
  }

  changeSizepage (rpp) {
    this.owner.getContext().put(util.format('GRID_PAGE%%%s', this.name), 0)
    this.owner.getContext().put(util.format('GRID_SIZE%%%s', this.name), rpp)
    this.owner.refresh()
  }

  orderColumn (colname) {
    var orderTxt
    var orderList = this.order
    if (orderList.indexOf(colname) !== -1) {
      orderList.splice(orderList.indexOf(colname), 1)
      colname = '-' + colname
    } else if (orderList.indexOf('-' + colname) !== -1) {
      orderList.splice(orderList.indexOf('-' + colname), 1)
    }
    orderTxt = orderList.join()
    if (orderTxt !== '') {
      orderTxt = colname + ',' + orderTxt
    } else {
      orderTxt = colname
    }
    this.owner.getContext().put(util.format('GRID_ORDER%%%s', this.name), orderTxt)
    this.owner.refresh()
  }

  getColumnOrder (colname) {
    var ret = 0
    if (this.order.indexOf(colname) !== -1) {
      ret = 1
    } else if (this.order.indexOf('-' + colname) !== -1) {
      ret = -1
    }
    return ret
  }

  dbclick () {
    if ((this.buttons.length > 0) && (this.getSelectedId().length === 1)) {
      var iBtn
      var selBtn = -1
      this.selectChange()
      for (iBtn = this.buttons.length - 1; iBtn >= 0; iBtn--) {
        if (this.buttons[iBtn].btnaction.mSelect !== SELECT_NONE) {
          selBtn = iBtn
        }
      }
      if (selBtn !== -1) {
        this.buttons[selBtn].actionPerformed()
      }
    }
  }

  fillValue (params) {
    var withGridval = false
    var isMulti = false
    var iBtn
    for (iBtn = 0; iBtn < this.buttons.length; iBtn++) {
      if ((this.buttons[iBtn].hasBeenClicked) && (this.buttons[iBtn].btnaction.mSelect !== SELECT_NONE)) {
        withGridval = true
        isMulti = (this.buttons[iBtn].btnaction.mSelect === SELECT_MULTI)
      }
    }
    if (withGridval) {
      if (this.getValue() === '') {
        throw new LucteriosException(MINOR, Singleton().getTranslate('Select one line before!'))
      }
      if (!isMulti && (this.getSelectedId().length > 1)) {
        throw new LucteriosException(MINOR, Singleton().getTranslate('Select only one line!'))
      }
      params.put(this.name, this.getValue())
    }
  }

  getHtml () {
    var html = ''
    if (this.description !== '') {
      html += util.format('<label for="%s">', this.getIdent())
      html += this.description
      html += '</label>'
      html += '<lct-cell>'
      html += '<lct-ctrl>'
      html += this.getSubHtml()
      html += '</lct-ctrl>'
    } else {
      html += '<lct-cell>'
      html += this.getSubHtml()
    }
    html += '</lct-cell>'
    return html
  }
}
