/*global $,unusedVariables,Class,compGeneric,format_to_string,Singleton,compButton,SELECT_MULTI,SELECT_SINGLE,SELECT_NONE,LucteriosException,MINOR*/

var compGridHeader = Class.extend({
	name : "",
	type : "",
	orderable : 0,
	label : "",
	formatstr : "{0}",
	grid : null,

	initial : function(headcomp, grid) {
		this.name = headcomp[0];
		this.label = headcomp[1];
		this.type = headcomp[2];
		this.orderable = headcomp[3];
		this.formatstr = (headcomp[4] || "{0}").replace(/%s/g, "{0}");
		this.grid = grid;
	},

	getid : function() {
		return 'grid-{0}_head-{1}'.format(this.grid.name, this.name.replace('.', '__'));
	},

	getHtml : function() {
		var headclass = '', sort_val, sort = '';
		if (this.orderable === 1) {
			headclass = " class_header";
			sort_val = this.grid.get_column_order(this.name.replace('.', '__'));
			if (sort_val > 0) {
				sort = '<span class="ui-icon ui-icon-triangle-1-n">&nbsp;</span>';
			}
			if (sort_val < 0) {
				sort = '<span class="ui-icon ui-icon-triangle-1-s">&nbsp;</span>';
			}
		}
		return '<th id="{0}" class="{1}">{2}{3}</th>'.format(this.getid(), headclass, this.label, sort);
	},

	addAction : function() {
		if (this.orderable === 1) {
			var current_comp = $("#" + this.getid());
			current_comp.click($.proxy(function() {
				this.grid.order_column(this.name.replace('.', '__'));
			}, this));
		}
	}
});

var compGridValue = Class.extend({
	name : "",
	value : "",
	parentGrid : "",

	initial : function(name, value) {
		this.name = name;
		this.value = value;
	},

	setParentGrid : function(grid) {
		this.parentGrid = grid;
	},

	getHtml : function() {
		var cell_type, label;
		if (this.value === "") {
			return '<td></td>';
		}
		cell_type = this.parentGrid.getValueType(this.name);
		if (cell_type === 'icon') {
			return '<td><img src="{0}"></td>'.format(Singleton().Transport().getIconUrl(this.value));
		}

		label = format_to_string(this.value, cell_type, this.parentGrid.getFormatStr(this.name));
		return '<td>{0}</td>'.format(label.convertLuctoriosFormatToHtml());
	}
});

var compGridRow = Class.extend({
	id : 0,
	values : null,
	grid : "",
	row_idx : 0,
	color_idx : 0,

	initial : function(row_idx, rowcomp, grid, color_idx) {
		this.row_idx = row_idx;
		this.color_idx = color_idx;
		this.grid = grid;
		this.id = rowcomp.id;

		var iCol, col_name, val;
		this.values = [];
		for (iCol = 0; iCol < this.grid.grid_headers.length; iCol++) {
			col_name = this.grid.grid_headers[iCol].name;
			val = new compGridValue();
			val.initial(col_name, rowcomp[col_name]);
			val.setParentGrid(this.grid);
			this.values[this.values.length] = val;
		}
	},

	getHtml : function() {
		var html, idx_val;
		html = '<tr id="{0}_{1}" pq-row-indx="{2}" class="{3}">'.format(this.grid.name, this.id, this.row_idx, (this.color_idx % 2) === 0 ? "odd"
				: "");
		for (idx_val = 0; idx_val < this.values.length; idx_val++) {
			html += this.values[idx_val].getHtml();
		}
		html += '</tr>';
		return html;
	},

	selectGridRow : function(event) {
		this.grid.changeSelectRow(this.row_idx, !this.isSelected(), event.shiftKey);
	},

	dbClickRow : function() {
		this.grid.clear_select_row(true);
		var row = $('#{0}_{1}'.format(this.grid.name, this.id));
		row.addClass("selected");
		this.grid.dbclick();
	},

	setSelected : function(select) {
		var row = $('#{0}_{1}'.format(this.grid.name, this.id));
		if (select) {
			row.addClass("selected");
		} else {
			row.removeClass("selected");
		}
	},

	isSelected : function() {
		var row = $('#{0}_{1}'.format(this.grid.name, this.id));
		return row.hasClass("selected");
	},

	addAction : function() {
		var row = $('#{0}_{1}'.format(this.grid.name, this.id));
		row.click($.proxy(this.selectGridRow, this));
		row.dblclick($.proxy(this.dbClickRow, this));
	}

});

var compGrid = compGeneric
		.extend({

			args : {},
			buttons : null,
			has_multi : false,
			has_select : false,
			page_max : 1,
			page_num : 0,
			size_by_page : 25,
			nb_lines : 0,
			grid_headers : null,
			grid_Rows : null,
			sortIndx : [],
			sortDir : [],
			last_row_selected : -1,

			initial : function(component) {
				this._super(component);
				this.tag = 'div';
				this.page_max = parseInt(component.page_max, 10) || 1;
				this.page_num = parseInt(component.page_num, 10) || 0;
				this.size_by_page = parseInt(component.size_by_page, 10) || 25;
				this.nb_lines = parseInt(component.nb_lines, 10) || 0;
				this.no_pager = component.no_pager || false;
				this.selectedList = [];

				this._order_manage(component);
				this._header_manage(component);
				this._rows_manage(component);
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

			_header_manage : function(component) {
				var heads = component.headers, iChild, header;
				this.grid_headers = [];
				for (iChild = 0; iChild < heads.length; iChild++) {
					header = new compGridHeader();
					header.initial(heads[iChild], this);
					this.grid_headers[this.grid_headers.length] = header;
				}
			},

			getValueType : function(name) {
				var iCol;
				for (iCol = 0; iCol < this.grid_headers.length; iCol++) {
					if (this.grid_headers[iCol].name === name) {
						return this.grid_headers[iCol].type;
					}
				}
				// ne devrait jamais arriver mais par defaut, on retourne null
				return null;
			},
			getFormatStr : function(name) {
				var iCol;
				for (iCol = 0; iCol < this.grid_headers.length; iCol++) {
					if (this.grid_headers[iCol].name === name) {
						return this.grid_headers[iCol].formatstr;
					}
				}
				return "{0}";
			},

			_rows_manage : function(component) {
				var iChild, row, color_idx = 0;
				this.grid_Rows = [];
				for (iChild = 0; iChild < component.value.length; iChild++) {
					if (iChild > 0) {
						if ((component.value[iChild].__color_ref__ === null)
								|| (component.value[iChild].__color_ref__ !== component.value[iChild - 1].__color_ref__)) {
							color_idx++;
						}
					}
					row = new compGridRow();
					row.initial(iChild, component.value[iChild], this, color_idx);
					this.grid_Rows[this.grid_Rows.length] = row;
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
						btn.notify_performed = $.proxy(this._save_scroll, this);
						btn.description = '';
						btn.action = Singleton().CreateAction();
						btn.action.initialize(this.owner, Singleton().Factory(), component.actions[iChild]);
						if (btn.action.mSelect === SELECT_MULTI) {
							this.has_multi = true;
						}
						if (btn.action.mSelect !== SELECT_NONE) {
							this.has_select = true;
						}
						btn.isMini = (btn.action.getTitle() === '');
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

			setValue : function(jsonvalue) {
				this.initial(jsonvalue);
				this.getGUIComp().html(this.get_Html());
			},

			get_pager_html : function() {
				var rppindex, rPPOptions = [ 25, 50, 100, 250, 500 ], html = '', attribdisabled = 'ui-button-disabled ui-state-disabled" disabled=""';
				if (!this.no_pager) {
					html = '<div class="gridpager" id="' + this.name + '_pager">';
					html += '<button type="button" title="{0}" class="ui-button ui-corner-all ui-widget ui-button-icon-only {1} style="margin-left: 10px;"><span class="ui-button-icon ui-icon ui-icon-seek-first"></span><span class="ui-button-icon-space"></span></button>'
							.format(Singleton().getTranslate("FirstPage"), this.page_num === 0 ? attribdisabled : '"');
					html += '<button type="button" title="{0}" class="ui-button ui-corner-all ui-widget ui-button-icon-only {1}><span class="ui-button-icon ui-icon ui-icon-seek-prev"></span><span class="ui-button-icon-space"></span></button>'
							.format(Singleton().getTranslate("PrevPage"), this.page_num === 0 ? attribdisabled : '"');
					html += '<span class="gridseparator"></span>';
					html += '<span>Page</span><input tabindex="0" class="ui-corner-all" type="text" value="{0}"><span>/</span><span class="total">{1}</span></span>'
							.format(this.page_num + 1, this.page_max);
					html += '<span class="gridseparator"></span>';
					html += '<button type="button" title="{0}" class="ui-button ui-corner-all ui-widget ui-button-icon-only {1}"><span class="ui-button-icon ui-icon ui-icon-seek-next"></span><span class="ui-button-icon-space"> </span></button>'
							.format(Singleton().getTranslate("NextPage"), (this.page_num + 1) === this.page_max ? attribdisabled : '"');
					html += '<button type="button" title="{0}" class="ui-button ui-corner-all ui-widget ui-button-icon-only {1}"><span class="ui-button-icon ui-icon ui-icon-seek-end"></span><span class="ui-button-icon-space"> </span></button>'
							.format(Singleton().getTranslate("LastPage"), (this.page_num + 1) === this.page_max ? attribdisabled : '"');
					html += '<span class="gridseparator"></span>';
					html += '<span>{0}</span><select class="ui-corner-all">'.format(Singleton().getTranslate("Rpp")).format('');
					for (rppindex = 0; rppindex < rPPOptions.length; rppindex++) {
						html += '<option value="{0}" {1}>{0}</option>'.format(rPPOptions[rppindex],
								rPPOptions[rppindex] === this.size_by_page ? "selected" : "");
					}
					html += '</select></span>';
					html += '<span class="gridseparator"></span>';
					if (this.nb_lines > 0) {
						html += '<span class="pq-pager-msg">{0}</span>'.format(Singleton().getTranslate("Display")).format(
								this.page_num * this.size_by_page + 1, Math.min((this.page_num + 1) * this.size_by_page, this.nb_lines),
								this.nb_lines);
					} else {
						html += '<span class="pq-pager-msg"></span>';
					}
					html += '</div>';
				}
				return html;
			},

			get_Html : function() {
				var iBtn, iRow, iHead, html = '', style = '';
				html = '<div name="{0}" {1}>'.format(this.name, style);
				if (this.buttons.length > 0) {
					html += '<div class="gridActions" id="' + this.name + '_actions">';
					for (iBtn = 0; iBtn < this.buttons.length; iBtn++) {
						html += this.buttons[iBtn].get_Html();
					}
					html += '</div>';
				}
				html += this.get_pager_html();
				html += '<div class="gridContent {0}">'.format(!this.no_pager ? 'gridscroll' : '');
				html += '<table cellspacing="0" cellpadding="0"><thead><tr>';
				for (iHead = 0; iHead < this.grid_headers.length; iHead++) {
					html += this.grid_headers[iHead].getHtml();
				}
				html += '</tr></thead><tbody>';
				if (this.grid_Rows.length === 0) {
					html += '<tr class="gridempty"><td colspan="{0}">{1}</td></tr>'.format(this.grid_headers.length, Singleton().getTranslate(
							"NoRows"));
				} else {
					for (iRow = 0; iRow < this.grid_Rows.length; iRow++) {
						html += this.grid_Rows[iRow].getHtml();
					}
				}
				html += '</tbody></table></div>';
				html += '</div>';
				return html;
			},

			addAction : function() {
				var iCol, iRow, iBtn, pqPager;
				for (iCol = 0; iCol < this.grid_headers.length; iCol++) {
					this.grid_headers[iCol].addAction();
				}
				for (iRow = 0; iRow < this.grid_Rows.length; iRow++) {
					this.grid_Rows[iRow].addAction();
				}
				for (iBtn = 0; iBtn < this.buttons.length; iBtn++) {
					this.buttons[iBtn].addAction();
					this.buttons[iBtn].setSelectType(SELECT_NONE);
				}
				pqPager = $("#" + this.owner.getId()).find("div[id='{0}_pager']:eq(0)".format(this.name));
				pqPager.find("span.ui-icon-seek-first").parent().click($.proxy(function() {
					this.change_numpage(0);
				}, this));
				pqPager.find("span.ui-icon-seek-prev").parent().click($.proxy(function() {
					this.change_numpage(this.page_num - 1);
				}, this));
				pqPager.find("span.ui-icon-seek-next").parent().click($.proxy(function() {
					this.change_numpage(this.page_num + 1);
				}, this));
				pqPager.find("span.ui-icon-seek-end").parent().click($.proxy(function() {
					this.change_numpage(this.page_max - 1);
				}, this));
				pqPager.find("input").change($.proxy(function(event) {
					this.change_numpage(parseInt(event.currentTarget.value, 10) - 1);
				}, this));
				pqPager.find("select").change($.proxy(function(event) {
					this.change_sizepage(event.currentTarget.value);
				}, this));
				this._load_scroll();
			},

			_load_scroll : function() {
				var div_scroll, scroll_pos = $("#" + this.owner.getId()).prop('scroll_{0}'.format(this.name));
				if (scroll_pos !== undefined) {
					div_scroll = $("#" + this.owner.getId()).find("div.gridContent:eq(0)");
					div_scroll[0].scrollTop = scroll_pos;
				}
			},

			_save_scroll : function() {
				var div_scroll = $("#" + this.owner.getId()).find("div.gridContent:eq(0)");
				$("#" + this.owner.getId()).prop('scroll_{0}'.format(this.name), div_scroll[0].scrollTop);
			},

			gui_finalize : function() {
				return;
			},

			clear_select_row : function(allclear) {
				if (!this.has_multi || allclear) {
					var iRow;
					for (iRow = 0; iRow < this.grid_Rows.length; iRow++) {
						this.grid_Rows[iRow].setSelected(false);
					}
				}
			},

			getSelectedId : function() {
				var selectedList = [], iRow;
				for (iRow = 0; iRow < this.grid_Rows.length; iRow++) {
					if (this.grid_Rows[iRow].isSelected()) {
						selectedList.push(this.grid_Rows[iRow].id);
					}
				}
				return selectedList;
			},

			changeSelectRow : function(rowidx, new_select_val, with_range) {
				if (!this.has_select) {
					return;
				}
				if (new_select_val) {
					this.clear_select_row(false);
				}
				if (with_range && (this.last_row_selected !== -1) && (this.last_row_selected !== rowidx)) {
					var row_idx, min_row = Math.min(this.last_row_selected + 1, rowidx), max_row = Math.max(this.last_row_selected - 1, rowidx);
					for (row_idx = min_row; row_idx <= max_row; row_idx++) {
						this.grid_Rows[row_idx].setSelected(new_select_val);
					}
				} else {
					this.grid_Rows[rowidx].setSelected(new_select_val);
				}
				this.last_row_selected = rowidx;
				this.selectChange();
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

			change_numpage : function(newPage) {
				this.owner.getContext().put('GRID_PAGE%{0}'.format(this.name), newPage);
				this.owner.getContext().put('GRID_SIZE%{0}'.format(this.name), this.size_by_page);
				this.owner.refresh();
			},

			change_sizepage : function(rpp) {
				this.owner.getContext().put('GRID_PAGE%{0}'.format(this.name), 0);
				this.owner.getContext().put('GRID_SIZE%{0}'.format(this.name), rpp);
				this.owner.refresh();
			},

			order_column : function(colname) {
				var order_txt, order_list = this.order;
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
			},

			get_column_order : function(colname) {
				var ret = 0;
				if (this.order.indexOf(colname) !== -1) {
					ret = 1;
				} else if (this.order.indexOf('-' + colname) !== -1) {
					ret = -1;
				}
				return ret;
			},

			dbclick : function() {
				if ((this.buttons.length > 0) && (this.getSelectedId().length === 1)) {
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
