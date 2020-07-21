/*global $,Class, screen, unusedVariables, Singleton, String, createGuid, Singleton*/

$.widget("ui.timespinner", $.ui.spinner, {
	options : {
		step : 1,
		page : 60,
		min : 0,
		max : 24 * 60
	},
	_parse : function(value) {
		if (typeof value === "string") {
			var time = value.split(':');
			return parseInt(time[0], 10) * 60 + parseInt(time[1], 10);
		}
		return value;
	},

	_format : function(value) {
		"use strict";
		var current_hour = Math.floor(value / 60), current_min = value - current_hour * 60;
		return "{0}:{1}".format(current_hour.toString().lpad('0', 2), current_min.toString().lpad('0', 2));
	}
});

$(document).delegate('.ui-dialog', 'keyup', function(e) {
	var tagName = e.target.tagName.toLowerCase();
	tagName = (tagName === 'input' && e.target.type === 'button') ? 'button' : tagName;
	if (e.which === $.ui.keyCode.ENTER && tagName !== 'textarea' && tagName !== 'select' && tagName !== 'button') {
		$(this).find('.ui-dialog-buttonset button').eq(0).trigger('click');
		return false;
	}
});

var GUIBasic = Class.extend({
	mId : '',
	mTitle : '',
	mHtmlBody : '',

	init : function(aId, aTitle, aCallback) {
		this.mId = aId;
		this.mTitle = aTitle;
		this.mCallback = aCallback;
	},

	isExist : function() {
		var item = document.getElementById(this.mId);
		return (item !== null);
	},

	close : function() {
		if (this.mCallback !== null) {
			this.mCallback.close(true);
		} else {
			this.dispose();
		}
	},

	dispose : function() {
		if (document.getElementById(this.mId) !== null) {
			$("#" + this.mId).remove();
		}
	},

	getHtmlDom : function() {
		return $("#" + this.mId);
	},

	buildStruct : function(isModal) {
		unusedVariables(isModal);
	},

	correctStruct : function() {
		return undefined;
	},

	buildFinal : function() {
		return undefined;
	},

	showGUI : function(isModal) {
		var not_exist = !this.isExist(), html = "";
		if (not_exist) {
			html += '<div id="{0}" title="{1}">'.format(this.mId, this.mTitle);
		}
		html += this.mHtmlBody;
		if (not_exist) {
			html += '</div>';
			$("#lucteriosClient").append(html);
			this.buildStruct(isModal);
		} else {
			$("#" + this.mId).html(html);
			this.correctStruct();
		}
		this.buildFinal();
	},

	setActive : function(aIsActive) {
		$("#" + this.mId).prop("disabled", !aIsActive);
		$("#{0} .class_controle".format(this.mId)).prop("disabled", !aIsActive);
		if (aIsActive) {
			$("#" + this.mId).css("cursor", "default");
		} else {
			$("#" + this.mId).css("cursor", "progress");
		}
	},

	moveCenter : function() {
		var dlg = $("#" + this.mId).parent(), new_left = (screen.width / 2) - (dlg.width() / 2), new_top = (screen.height / 2) - (dlg.height() / 2);
		dlg.offset({
			top : new_top,
			left : new_left
		});
	}

});

var GUIManage = GUIBasic.extend({
	mButtons : [],
	withForm : false,
	defaultbtn : '',

	addcontent : function(aHtmlBody, aButtons) {
		if (this.withForm) {
			this.mHtmlBody = '<form id="frm_{0}">{1}</form>'.format(this.mId, aHtmlBody);
		} else {
			this.mHtmlBody = aHtmlBody;
		}
		this.mButtons = aButtons;
	},

	get_button_list : function() {
		var buttonlist = [], iAct, new_button = {};
		for (iAct = 0; iAct < this.mButtons.length; iAct += 1) {
			buttonlist[buttonlist.length] = this.mButtons[iAct].get_button();
		}

		if (buttonlist.length === 0) {
			new_button = {
				text : Singleton().getTranslate("Close")
			};
			if (this.mCallback !== null) {
				new_button.click = $.proxy(function() {
					this.close(true);
				}, this.mCallback);
			} else {
				new_button.click = function() {
					$(this).dialog("close");
				};
			}
			buttonlist = [ new_button ];
		}
		return buttonlist;
	},

	buildStruct : function(isModal) {
		var args = {}, titlebar = null;
		args = {
			title : this.mTitle,
			width : 'auto',
			height : 'auto',
			modal : isModal,
			classes : {
				"ui-dialog" : "lct-dialog",
				"ui-dialog-content" : "lct-dlgcontent",
				"ui-dialog-buttonpane" : "lct-dlgbtnpn",
				"ui-dialog-buttonset" : "lct-dlgbtnset"
			},
			resize: $.proxy(function(event, ui) {
				unusedVariables(event, ui);
				var tabid;
				this.change_size_childreen();
				if ((this.mCallback !== null) && (this.mCallback.gui_finalize !== undefined)) {
					this.mCallback.gui_finalize(0);
					tabid = $("#" + this.mCallback.getId()).prop('tabid');
					if (tabid !== undefined) {
						this.mCallback.gui_finalize(tabid+1);
					} else {
						this.mCallback.gui_finalize(1);
					}																
				}				
			},this),
			buttons : this.get_button_list(),
			close : $.proxy(function(event, ui) {
				unusedVariables(event, ui);
				this.close();
			}, this)
		};
		if (!isModal) {
			args.width = 1200;
			args.height = 600;					
		}
		$("#" + this.mId).dialog(args);
		if (isModal) {
			$("#" + this.mId).css('max-height', String($(window).height()-150)+'px');
			$("#" + this.mId).parent().css('top', String(($(window).height()-$("#" + this.mId).parent().height())/2)+'px');
		}
		if (this.mCallback !== null) {
			titlebar = $("#" + this.mId).parent().find('.ui-dialog-titlebar');
			$('<button id="refresh_'+ this.mId + '" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-icon-only ui-dialog-titlebar-refresh" role="button" aria-disabled="false" title="refresh"></button>')
					.append('<span class="ui-button-icon-primary ui-icon ui-icon-refresh"/>')
					.append('<span class="ui-button-text">refresh</span>')
					.appendTo(titlebar)
					.hover(function() {$(this).addClass('ui-state-hover');}, function() {$(this).removeClass('ui-state-hover');})
					.click($.proxy(function() {this.refresh();}, this.mCallback));
			if (!isModal) {
				$('<button id="fullscreen_'+ this.mId + '" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-icon-only ui-dialog-titlebar-fullscreen" role="button" aria-disabled="false" title="full"></button>')
						.append('<span class="ui-button-icon-primary ui-icon ui-icon-arrow-4-diag"/>')
						.append('<span class="ui-button-text">full</span>')
						.appendTo(titlebar);
				$("#fullscreen_"+ this.mId).click($.proxy(this.fullscreen, this));
			}
		}
		$("#" + this.mId).keyup($.proxy(this.manageKey, this));
		$("#" + this.mId).css("padding", "0em .5em 2em .5em");
	},
	
	resize_screen : function(width, height, top, left) {
		var id_hgt, parent_hgt, diff_hgt;
		id_hgt = $("#"+this.mId).height();
		parent_hgt=$("#"+this.mId).parent().height();
		$("#"+this.mId).parent().css({
	        'width': width,
	        'height': height,
	        'left': left,
	        'top': top									
		});
		diff_hgt = $("#"+this.mId).parent().height() - parent_hgt;
		$("#"+this.mId).height(id_hgt+diff_hgt);
	},
	
	fullscreen : function() {
		var new_width, new_height, new_top, new_left, old_size=$("#"+this.mId).data('old_size');
		if ((old_size === undefined) || (old_size === null)) {
			new_width = $(document).width();
			new_height = $(document).height();
			new_top = '0px';
			new_left = '0px'; 
			$("#"+this.mId).data('old_size', [$("#"+this.mId).parent().width(),$("#"+this.mId).parent().height(),$("#"+this.mId).parent().css('top'),$("#"+this.mId).parent().css('left')]);
		} else {
			new_width = old_size[0];
			new_height = old_size[1];
			new_top = old_size[2];
			new_left = old_size[3];
			$("#"+this.mId).data('old_size', null);
		}
		this.resize_screen(new_width, new_height, new_top, new_left);
	},

	manageKey : function(event) {
		var btn;
		if ((event.keyCode === 13) && (this.defaultbtn !== '')) {
			btn = $("#" + this.mCallback.getId()).find(this.defaultbtn);
			if (btn.length === 1) {
				btn.click();
                btn.focusout();                                                                  
                btn.change();                                               
			}
		}
	},

	correctStruct : function() {
		if ($("#" + this.mId).hasClass("ui-dialog-content")) {
			$("#" + this.mId).dialog('option', 'buttons', this.get_button_list());
		}
	},

	buildFinal : function() {
		var parent = $("#" + this.mId).parent(), iAct, btn_icon, btn, callback=this.mCallback;
		$("#" + this.mId + " .tabContent").each(function() {
			$(this).tabs({
				activate : $.proxy(function(event, ui) {
					var tabid = ui.newTab.index();
					unusedVariables(event);
					this.parent().prop('tabid', tabid);
					if ((callback !== null) && (callback.gui_finalize !== undefined)) {
						callback.gui_finalize(tabid+1);
					}				
				}, $(this))
			});
		});
		$(".datepicker").each(function() {
			$(this).datepicker({
				showOn : "button",
				buttonImage : "images/calendar.png",
				buttonImageOnly : true,
				changeMonth : true,
				changeYear : true,
				dateFormat : 'dd/mm/yy'
			}, $.datepicker.regional.fr);
		});
		$(".timespinner").each(function() {
			$(this).timespinner();
		});
		for (iAct = 0; iAct < this.mButtons.length; iAct++) {
			if (this.mButtons[iAct].getIcon() !== '') {
				btn_icon = this.mButtons[iAct].getIcon();
				if (btn_icon.startsWith('/static/')) {
					btn_icon = Singleton().Transport().getIconUrl(btn_icon);
				}
				btn = parent.find("div > div.lct-dlgbtnset > button:eq({0})".format(iAct));
				btn.find('img').remove();
				btn.prepend('<img height="24px" src="{0}" />'.format(btn_icon));
			}
		}
		if (this.mButtons.length === 0) {
			btn = parent.find("div > div.lct-dlgbtnset > button:eq(0)");
			if ((btn.length === 1) && (parent.find("div > div > button:eq(1)").length === 0)) {
				btn_icon = "images/close.png";
				btn.find('img').remove();
				btn.prepend('<img height="24px" src="{0}" />'.format(btn_icon));
			}
		}
		this.change_size_childreen();
	},

	change_size_childreen : function() {
		var childreen, height, sum_height=0, child_idx, new_height;
		$("#"+this.mId).data('size', [$("#"+this.mId).parent().width(),$("#"+this.mId).parent().height(),$("#"+this.mId).parent().css('top'),$("#"+this.mId).parent().css('left')]);
		childreen = $("#" + this.mId)[0].childNodes;
		if (childreen.length>1) {
			for(child_idx=0;child_idx<childreen.length;child_idx++) {
				sum_height=sum_height+childreen[child_idx].clientHeight;
			}
			height=$("#" + this.mId)[0].clientHeight;
			new_height = childreen[childreen.length-1].clientHeight + height - sum_height - 50;
			childreen[childreen.length-1].style["min-height"] = new_height+"px";
		}
	},

	reloadSize : function() {
		var new_width, new_height, new_top, new_left, current_size=$("#"+this.mId).data('size');
		if ((current_size !== undefined) && (current_size !== null)) {
			new_width = current_size[0];
			new_height = current_size[1];
			new_top = current_size[2];
			new_left = current_size[3];
			this.resize_screen(new_width, new_height, new_top, new_left);
		}
	},
	
	dispose : function() {
		if (document.getElementById(this.mId) !== null) {
			$("#" + this.mId).dialog("destroy");
			$("#" + this.mId).remove();
		}
	}

});

String.prototype.convertLuctoriosFormatToHtml = function() {
	var text = this.replace(">", "&gt;");
	text = text.replace(/</g, "&lt;");
	text = text.replace(/\{\[bold\]\}/g, "<b>");
	text = text.replace(/\{\[\/bold\]\}/g, "</b>");
	text = text.replace(/\{\[italc\]\}/g, "<i>");
	text = text.replace(/\{\[\/italc\]\}/g, "</i>");
	text = text.replace(/\{\[italic\]\}/g, "<i>");
	text = text.replace(/\{\[\/italic\]\}/g, "</i>");
	text = text.replace(/\{\[newline\]\}/g, "<br>");
	text = text.replace(/\{\[underline\]\}/g, "<u>");
	text = text.replace(/\{\[\/underline\]\}/g, "</u>");
	text = text.replace(/\{\[center\]\}/g, "<center>");
	text = text.replace(/\{\[\/center\]\}/g, "</center>");
	text = text.replace(/\{\[hr\/\]\}/g, "<hr/>");
	text = text.replace(/<hr>/g, "<hr/>");
	text = text.replace(/\{\[br\/\]\}/g, "<br/>");
	text = text.replace(/\{\[/g, "<");
	text = text.replace(/\]\}/g, ">");
	if ((text.length > 0) && text.charAt(0) === '/') {
		text = "&#47;" + text.substring(1);
	}
	return text;
};

String.prototype.convertHtmlToLuctoriosFormat = function() {
	var text = this.replace(/\n/g, '{[newline]}');
	text = text.replace(/<br>/g, '{[newline]}');
	text = text.replace(/</g, '{[');
	text = text.replace(/>/g, ']}');
	return text;
};

function format_value(value, format_num) {
	var options=null, sub_format=null;
	if ((value!==null) && (typeof value === "object")) {
		if (value.hasOwnProperty('format')) {
			sub_format = value.format;
		}
		if (value.hasOwnProperty('value')) {
			value = value.value;
		} else {
			value = null;
		}
	}
	
	if (value===null) {
		value = "---";
		format_num = '';
	}	
	if (typeof format_num === "object") {
		if (format_num.hasOwnProperty(value)) {
			value = format_num[value];
		}
		format_num = '';
	}
	if (format_num==='B') {
		if (value === true) {
			value = Singleton().getTranslate("Yes");
		} else {
			value = Singleton().getTranslate("No");
		}
	}
	if (format_num==='T') {
		value = new Date("1900-01-01 "+value);
		options = { hour: "2-digit", minute: "2-digit"};
	}
	if (format_num==='D') {
		value = new Date(value);
		options = { year: 'numeric', month: 'long', day: "numeric"};
	}
	if (format_num==='H') {
		value = new Date(value);
		options = {weekday:'long', year: 'numeric', month: 'long', day: "numeric", hour: "2-digit", minute: "2-digit"};
	}	
	if (format_num.substr(0, 1) === "N") {
		value = Number(value);
		options = { minimumFractionDigits : Number(format_num.substr(1)), maximumFractionDigits : Number(format_num.substr(1))};
	}
	if (format_num.substr(0, 1) === "C") {
		value = Number(value);
		options = { minimumFractionDigits: Number(format_num.substr(1,1)), maximumFractionDigits : Number(format_num.substr(1,1)),
				style: "currency", currency: format_num.substr(2), currencyDisplay: "symbol"};
	}
	if (options!==null) {
		value = value.toLocaleString(Singleton().getSelectLang(), options);
	}
	if (sub_format!==null) {
		value = sub_format.format(value);
	}
	return value;
}

function format_to_string(value, format_num, format_str) {
	var val_idx;
	if (format_num===null) {
		format_num = '';
	}
	if (format_str===null) {
		format_str = '{0}';
	}
	if (format_str.indexOf(";") !== -1) {
		format_str = format_str.split(';');
		if ((Math.abs(Number(value))<0.00001) && (format_str.length > 2)) {
			format_str = format_str[2];
			value = Number(value);
		} else {
			if ((Number(value)<0.00001) && (format_str.length > 1)) {
				format_str = format_str[1];
				value = Math.abs(Number(value));
			}
			else {
				format_str = format_str[0];
			}
		}
	}
		
	if (Array.isArray(value)) {
		for(val_idx=0;val_idx<value.length;val_idx++) {
			value[val_idx] = format_value(value[val_idx],format_num);
		}
		if (format_str.indexOf('{1}') === -1) {
			value=[value.join('{[br/]}')];
		}
	}
	else {
		value=[format_value(value,format_num)];
	}
	return format_str.format(...value);
}

var compBasic = Class.extend({
	colspan : 1,
	rowspan : 1,
	style : '',
	html : '',
	defvalue : function(aVal, aDefault) {
		if (aVal === undefined) {
			return aDefault;
		}
		return aVal;
	},

	init : function(aHtml, aColspan, aRowspan, aStyle) {
		this.html = this.defvalue(aHtml, '');
		this.colspan = this.defvalue(aColspan, 1);
		this.rowspan = this.defvalue(aRowspan, 1);
		this.style = this.defvalue(aStyle, '');
	},
	getHtml : function() {
		return this.html;
	}
});

function createTable(compArray) {
	// traitement de la grille de placement des elements
	var line, compo, html = '<table width="100%">', row_idx, col_idx, colspan_idx, rowspan_idx;
	for (row_idx = 0; row_idx < compArray.length; row_idx++) {
		if ((compArray[row_idx] instanceof Array) && (compArray[row_idx].length > 0)) {
			html += '<tr>';
			line = compArray[row_idx];
			for (col_idx = 0; col_idx < line.length; col_idx++) {
				if ((line[col_idx] !== undefined) && (line[col_idx] !== null)) {
					compo = line[col_idx];
					html += '<td rowspan="{0}" colspan="{1}" style="{2}">{3}</td>'.format(compo.rowspan, compo.colspan, compo.style, compo.getHtml());
					for (colspan_idx = 0; colspan_idx < compo.colspan; colspan_idx++) {
						line[col_idx + colspan_idx] = null;
						for (rowspan_idx = 0; rowspan_idx < compo.rowspan; rowspan_idx++) {
							if (!(compArray[row_idx + rowspan_idx] instanceof Array)) {
								compArray[row_idx + rowspan_idx] = [];
							}
							compArray[row_idx + rowspan_idx][col_idx + colspan_idx] = null;
						}
					}
				} else if (line[col_idx] === undefined) {
					html += '<td/>';
				}
			}
			html += '</tr>';
		}
	}
	html += '</table>';
	return html;
}

function createTab(tabs, tabcontents) {
	var tab_Id = createGuid(), html = "<div class='tabContent'>", t_idx, tabcontentvalue;
	html += "<ul>";
	for (t_idx = 0; t_idx < tabs.length; t_idx++) {
		html += '<li><a href="#tab_{0}_{1}">{2}</a></li>'.format(tab_Id, t_idx, tabs[t_idx]);
	}
	html += "</ul>";
	for (t_idx = 0; t_idx < tabcontents.length; t_idx++) {
		tabcontentvalue = tabcontents[t_idx];
		if (tabcontentvalue instanceof Array) {
			tabcontentvalue = createTable(tabcontentvalue);
		}
		html += '<div id="tab_{0}_{1}">{2}</div>'.format(tab_Id, t_idx, tabcontentvalue);
	}
	html += "</div>";
	return html;
}
