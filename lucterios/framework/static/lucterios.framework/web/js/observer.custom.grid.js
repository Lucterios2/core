/*global $,unusedVariables,compGeneric,Singleton,compButton,SELECT_MULTI,SELECT_SINGLE,SELECT_NONE,LucteriosException,MINOR*/

var compGrid = compGeneric.extend({

	args : {},
	buttons : null,
	has_multi : false,
	has_select : false,
	page_max : 1,
	page_num : 0,
	size_by_page : 25,
	nb_lines : 0,
	gridHeaders : null,
	gridRows : null,
	sortIndx : [],
	sortDir : [],

	initial : function(component) {
		this._super(component);
		this.tag = 'div';
		this.page_max = parseInt(component.page_max, 10) || 1;
		this.page_num = parseInt(component.page_num, 10) || 0;
		this.size_by_page = parseInt(component.size_by_page, 10) || 25;
		this.nb_lines = parseInt(component.nb_lines, 10) || 0;
		this.no_pager = component.no_pager || false;
		this.selectedList = [];

		this.gridRows = component.value;
		this._order_manage(component);
		this._header_manage(component);
		this._action_manage(component);
	},

	_order_manage : function(component) {
		var iChild;
		this.order = component.order || [];
		this.sortIndx = [];
		this.sortDir = [];
		for (iChild = 0; iChild < this.order.length; iChild++) {
			if (this.order[iChild].substring(0, 1) === '-') {
				this.sortIndx.push(this.order[iChild].substring(1));
				this.sortDir.push('down');
			} else {
				this.sortIndx.push(this.order[iChild]);
				this.sortDir.push('up');
			}
		}
	},

	_date_render : function(ui) {
		var value = ui.rowData[ui.dataIndx];
		if (value !== '---') {
			return new Date(value).toLocaleDateString(Singleton().getSelectLang(), {
				year : 'numeric',
				month : 'short',
				day : 'numeric'
			});
		}
		return "---";
	},

	_datetime_render : function(ui) {
		var value = ui.rowData[ui.dataIndx];
		if (value !== '---') {
			return new Date(value).toLocaleDateString(Singleton().getSelectLang(), {
				year : 'numeric',
				month : 'short',
				day : 'numeric',
				hour : 'numeric',
				minute : 'numeric'
			});
		}
		return "---";
	},

	_bool_render : function(ui) {
		var value = ui.rowData[ui.dataIndx];
		if ((value === '0') || (value.toLowerCase() === 'false') || (value === 'n')) {
			return '<input type="checkbox" disabled="1" ></input>';
		}
		return '<input type="checkbox"  disabled="1" checked="1" ></input>';
	},

	_icon_render : function(ui) {
		var value = ui.rowData[ui.dataIndx];
		return '<img src="{0}">'.format(Singleton().Transport().getIconUrl(value));
	},

	_default_render : function(ui) {
		return ui.rowData[ui.dataIndx].convertLuctoriosFormatToHtml();
	},

	_header_manage : function(component) {
		var heads = component.headers, iChild, header;
		this.gridHeaders = [];
		for (iChild = 0; iChild < heads.length; iChild++) {
			header = {
				title : heads[iChild][1],
				dataIndx : heads[iChild][0],
				resizable : true,
				orderable : heads[iChild][3]
			};
			switch (heads[iChild][2]) {
			case 'int':
				header.dataType = "integer";
				header.width = '5%';
				break;
			case 'float':
				header.dataType = "float";
				header.width = '5%';
				break;
			case 'datetime':
				header.width = '15%';
				header.render = this._datetime_render;
				break;
			case 'date':
				header.width = '15%';
				header.render = this._date_render;
				break;
			case 'bool':
				header.width = '5%';
				header.render = this._bool_render;
				break;
			case 'icon':
				header.render = this._icon_render;
				break;
			default:
				if (heads[iChild][1].length <= 2) {
					header.width = '3%';
				}
				header.render = this._default_render;
				break;
			}
			this.gridHeaders[this.gridHeaders.length] = header;
		}
	},

	_action_manage : function(component) {
		var iChild, btn;
		this.buttons = [];
		if (component.actions) {
			for (iChild = 0; iChild < component.actions.length; iChild++) {
				btn = new compButton(this.owner);
				btn.initial(component.actions[iChild]);
				btn.name = "{0}_{1}".format(this.name, iChild);
				btn.description = '';
				btn.action = Singleton().CreateAction();
				btn.action.initialize(this.owner, Singleton().Factory(), component.actions[iChild]);
				if (btn.action.mSelect === SELECT_MULTI) {
					this.has_multi = true;
				}
				if (btn.action.mSelect !== SELECT_NONE) {
					this.has_select = true;
				}
				this.buttons[this.buttons.length] = btn;
			}
		}
	},

	getValue : function() {
		var selectedList = this.getSelectedId();
		return selectedList.join(';');
	},

	initialVal : function() {
		return '';
	},

	setValue : function(xmlValue) {
		this.initial(xmlValue.parseXML());
		this.getGUIComp().html(this.get_Html());
	},

	get_Html : function() {
		var iBtn, html = '';
		if (this.buttons.length > 0) {
			html += '<div class="gridActions" id="' + this.name + '_actions">';
			for (iBtn = 0; iBtn < this.buttons.length; iBtn++) {
				html += this.buttons[iBtn].get_Html();
			}
			html += '</div>';
		}
		html += this.getBuildHtml(this.args, true, true);
		return html;
	},

	addAction : function() {
		var iBtn, obj, grid, pageModel, pqPager;
		for (iBtn = 0; iBtn < this.buttons.length; iBtn++) {
			this.buttons[iBtn].addAction();
			this.buttons[iBtn].setSelectType(SELECT_NONE);
		}

		pageModel = {
			type : "remote",
			rPP : this.no_pager ? this.gridRows.length : this.size_by_page,
			rPPOptions : [ 25, 50, 100, 250 ],
			totalPages : this.page_max,
			curPage : this.page_num + 1,
			totalRecords : this.nb_lines,
			change : $.proxy(this.changePage, this)
		};
		obj = {
			width : '97%',
			height: 300,
			collapsible : false,
			showTop : !this.no_pager,
			showTitle : false,
			showBottom : false,
			editable : false,
			virtualX : false,
			hoverMode : 'row',
			scrollModel : {
				autoFit : true
			},
			numberCell : {
				show : false
			},
			selectionModel : {
				type : 'null'
			},
			flexWidth : false,
			flexHeight : false,
			create : $.proxy(this.createGrid, this),
			pageModel : pageModel,
			resizable: true,
			wrap: true
		};
		if (this.has_select) {
			obj.selectionModel.type = 'row';
			if (!this.has_multi) {
				obj.selectionModel.mode = 'single';
			}
		}
		obj.colModel = this.gridHeaders;
		obj.columnTemplate = {
			minWidth : '1%',
			maxWidth : '99%'
		};
		obj.dataModel = {
			data : this.gridRows,
			type : "local",
			location : "local",
			url : null,
			sorting : "remote",
			sortIndx : this.sortIndx,
			sortDir : this.sortDir
		};
		obj.rowSelect = $.proxy(this.selectChange, this);
		obj.rowUnSelect = $.proxy(this.selectChange, this);
		obj.rowDblClick = $.proxy(this.dbclick, this);
		obj.beforeSort = $.proxy(this.order_col, this);

		obj.strLoading = Singleton().getTranslate("Loading");
		obj.strNoRows = Singleton().getTranslate("NoRows");

		pageModel.strFirstPage = Singleton().getTranslate("FirstPage");
		pageModel.strPrevPage = Singleton().getTranslate("PrevPage");
		pageModel.strNextPage = Singleton().getTranslate("NextPage");
		pageModel.strLastPage = Singleton().getTranslate("LastPage");
		pageModel.strRefresh = Singleton().getTranslate("Refresh");
		pageModel.strRpp = Singleton().getTranslate("Rpp");
		pageModel.strDisplay = Singleton().getTranslate("Display");

		grid = this.getGUIComp().pqGrid(obj);
		pqPager = grid.find("div.pq-pager").pqPager();
		pqPager.find("button:last").detach();
		pqPager.find("span.pq-separator:last").detach();
		pqPager.pqPager(pageModel);
	},

	gui_finalize : function() {
		this.getGUIComp().pqGrid("refresh");
		return;
	},

	createGrid : function() {
		var $grid = this.getGUIComp().pqGrid(), $pager = $grid.find(".pq-grid-bottom").find(".pq-pager");
		if ($pager && $pager.length) {
			$pager = $pager.detach();
			$grid.find(".pq-grid-top").append($pager);
		}
	},

	dbclick : function() {
		if ((this.buttons.length > 0) && (this.getSelectedId() > 0)) {
			var iBtn, sel_btn = -1;
			this.selectChange();
			for (iBtn = this.buttons.length - 1; iBtn >= 0; iBtn--) {
				if (this.buttons[iBtn].btnaction.mSelect !== SELECT_NONE) {
					sel_btn = iBtn;
				}
			}
			if (sel_btn !== -1) {
				this.buttons[sel_btn].actionPerformed();
			}
		}
	},

	getSelectedId : function() {
		var selectedList = [], iSel, selectionArray;
		selectionArray = this.getGUIComp().pqGrid("selection", {
			type : 'row',
			method : 'getSelection'
		});
		for (iSel = 0; iSel < selectionArray.length; iSel++) {
			selectedList.push(selectionArray[iSel].rowData.id);
		}
		return selectedList;
	},

	selectChange : function() {
		var selectedList = this.getSelectedId(), select_type, iBtn;
		if (selectedList.length === 0) {
			select_type = SELECT_NONE;
		} else if (selectedList.length === 1) {
			select_type = SELECT_SINGLE;
		} else {
			select_type = SELECT_MULTI;
		}
		for (iBtn = 0; iBtn < this.buttons.length; iBtn++) {
			this.buttons[iBtn].setSelectType(select_type);
		}
	},

	changePage : function(event, ui) {
		unusedVariables(event);
		if (ui.curPage) {
			this.owner.getContext().put('GRID_PAGE%{0}'.format(this.name), ui.curPage - 1);
			this.owner.getContext().put('GRID_SIZE%{0}'.format(this.name), this.size_by_page);
			this.owner.refresh();
		} else if (ui.rPP) {
			this.owner.getContext().put('GRID_PAGE%{0}'.format(this.name), 0);
			this.owner.getContext().put('GRID_SIZE%{0}'.format(this.name), ui.rPP);
			this.owner.refresh();
		}
	},

	order_col : function(event, ui) {
		unusedVariables(event);
		if (ui.column.orderable === 1) {
			var order_txt, colname = ui.dataIndx.replace('.', '__'), order_list = this.order;
			if (order_list.indexOf(colname) !== -1) {
				order_list.splice(order_list.indexOf(colname), 1);
				colname = '-' + colname;
			} else if (order_list.indexOf('-' + colname) !== -1) {
				order_list.splice(order_list.indexOf('-' + colname), 1);
			}
			order_txt = order_list.join();
			if (order_txt !== '') {
				order_txt = colname + ',' + order_txt;
			} else {
				order_txt = colname;
			}
			this.owner.getContext().put('GRID_ORDER%{0}'.format(this.name), order_txt);
			this.owner.refresh();
		}
		return false;
	},

	fillValue : function(params) {
		var with_gridval = false, is_multi = false, iBtn;
		for (iBtn = 0; iBtn < this.buttons.length; iBtn++) {
			if ((this.buttons[iBtn].hasBeenClicked) && (this.buttons[iBtn].btnaction.mSelect !== SELECT_NONE)) {
				with_gridval = true;
				is_multi = (this.buttons[iBtn].btnaction.mSelect === SELECT_MULTI);
			}
		}
		if (with_gridval) {
			if (this.getValue() === '') {
				throw new LucteriosException(MINOR, Singleton().getTranslate("Select one line before!"));
			}
			if (!is_multi && (this.getSelectedId().length > 1)) {
				throw new LucteriosException(MINOR, Singleton().getTranslate("Select only one line!"));
			}
			params.put(this.name, this.getValue());
		}
	},

	getHtml : function() {
		var html = "";
		if (this.description !== '') {
			html += "<label for='{0}'>".format(this.get_id());
			html += this.description;
			html += "</label>";
			html += "<lct-cell>";
			html += "<lct-ctrl>";
			html += this.get_Html();
			html += "</lct-ctrl>";
		} else {
			html += "<lct-cell>";
			html += this.get_Html();
		}
		html += "</lct-cell>";
		return html;
	}

});
