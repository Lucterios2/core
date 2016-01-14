/*global $,Class, screen, unusedVariables, Singleton, String, createGuid*/

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
		var current_hour = Math.floor(value / 60), current_min = value
				- current_hour * 60;
		return "{0}:{1}".format(current_hour.toString().lpad('0', 2),
				current_min.toString().lpad('0', 2));
	}
});

$(document)
		.delegate(
				'.ui-dialog',
				'keyup',
				function(e) {
					var tagName = e.target.tagName.toLowerCase();
					tagName = (tagName === 'input' && e.target.type === 'button') ? 'button'
							: tagName;
					if (e.which === $.ui.keyCode.ENTER
							&& tagName !== 'textarea' && tagName !== 'select'
							&& tagName !== 'button') {
						$(this).find('.ui-dialog-buttonset button').eq(0)
								.trigger('click');
						return false;
					}
				});

var GUIBasic = Class
		.extend({
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
					html += '<div id="{0}" title="{1}">'.format(this.mId,
							this.mTitle);
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
				$("#{0} .class_controle".format(this.mId)).prop("disabled",
						!aIsActive);
				if (aIsActive) {
					$("#" + this.mId).css("cursor", "default");
				} else {
					$("#" + this.mId).css("cursor", "progress");
				}
			},

			moveCenter : function() {
				var dlg = $("#" + this.mId).parent(), new_left = (screen.width / 2)
						- (dlg.width() / 2), new_top = (screen.height / 2)
						- (dlg.height() / 2);
				dlg.offset({
					top : new_top,
					left : new_left
				});
			}

		});

var GUIManage = GUIBasic
		.extend({
			mButtons : [],
			withForm : false,

			addcontent : function(aHtmlBody, aButtons) {
				if (this.withForm) {
					this.mHtmlBody = '<form id="frm_{0}">{1}</form>'.format(
							this.mId, aHtmlBody);
				} else {
					this.mHtmlBody = aHtmlBody;
				}
				this.mButtons = aButtons;
			},

			get_button_list : function() {
				var buttonlist = [], iAct, new_button = {};
				for (iAct = 0; iAct < this.mButtons.length; iAct += 1) {
					buttonlist[buttonlist.length] = this.mButtons[iAct]
							.get_button();
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
					buttons : this.get_button_list(),
					close : $.proxy(function(event, ui) {
						unusedVariables(event, ui);
						this.close();
					}, this)
				};
				if (!isModal) {
					args.width = 1000;
					args.height = 600;
				}
				$("#" + this.mId).dialog(args);
				if (this.mCallback !== null) {
					titlebar = $("#" + this.mId).parent().find(
							'.ui-dialog-titlebar');
					$(
							'<button id="refresh_'
									+ this.mId
									+ '" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-icon-only ui-dialog-titlebar-refresh" role="button" aria-disabled="false" title="refresh"></button>')
							.append(
									'<span class="ui-button-icon-primary ui-icon ui-icon-refresh"/>')
							.append(
									'<span class="ui-button-text">refresh</span>')
							.appendTo(titlebar).hover(function() {
								$(this).addClass('ui-state-hover');
							}, function() {
								$(this).removeClass('ui-state-hover');
							}).click($.proxy(function() {
								this.refresh();
							}, this.mCallback));
				}
			},

			correctStruct : function() {
				if ($("#" + this.mId).hasClass("ui-dialog-content")) {
					$("#" + this.mId).dialog('option', 'buttons',
							this.get_button_list());
				}
			},

			memorize_size : function() {
				var jcnt = this.getHtmlDom();
				jcnt[0].style.height = (jcnt[0].clientHeight + 10) + 'px';
				jcnt[0].style.width = (jcnt[0].clientWidth + 5) + 'px';
			},

			buildFinal : function() {
				var parent = $("#" + this.mId).parent(), iAct, btn_icon, btn;
				$(".tabContent").each(
						function() {
							$(this).tabs(
									{
										activate : $.proxy(function(event, ui) {
											unusedVariables(event);
											this.parent().prop('tabid',
													ui.newTab.index());
										}, $(this))
									});
							var tabid = $(this).parent().prop('tabid');
							if (tabid !== undefined) {
								$(this).find(
										'ul > li:eq({0}) > a'.format(tabid))
										.click();
							}
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
						btn_icon = Singleton().Transport().getIconUrl(
								this.mButtons[iAct].getIcon());
						btn = parent.find("div > div > button:eq({0}) > span"
								.format(iAct));
						btn.find('img').remove();
						btn.prepend('<img src="{0}" />'.format(btn_icon));
					}
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
		if ((compArray[row_idx] instanceof Array)
				&& (compArray[row_idx].length > 0)) {
			html += '<tr>';
			line = compArray[row_idx];
			for (col_idx = 0; col_idx < line.length; col_idx++) {
				if ((line[col_idx] !== undefined) && (line[col_idx] !== null)) {
					compo = line[col_idx];
					html += '<td rowspan="{0}" colspan="{1}" style="{2}">{3}</td>'
							.format(compo.rowspan, compo.colspan, compo.style,
									compo.getHtml());
					for (colspan_idx = 0; colspan_idx < compo.colspan; colspan_idx++) {
						line[col_idx + colspan_idx] = null;
						for (rowspan_idx = 0; rowspan_idx < compo.rowspan; rowspan_idx++) {
							if (!(compArray[row_idx + rowspan_idx] instanceof Array)) {
								compArray[row_idx + rowspan_idx] = [];
							}
							compArray[row_idx + rowspan_idx][col_idx
									+ colspan_idx] = null;
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
		html += '<li><a href="#tab_{0}_{1}">{2}</a></li>'.format(tab_Id, t_idx,
				tabs[t_idx]);
	}
	html += "</ul>";
	for (t_idx = 0; t_idx < tabcontents.length; t_idx++) {
		tabcontentvalue = tabcontents[t_idx];
		if (tabcontentvalue instanceof Array) {
			tabcontentvalue = createTable(tabcontentvalue);
		}
		html += '<div id="tab_{0}_{1}">{2}</div>'.format(tab_Id, t_idx,
				tabcontentvalue);
	}
	html += "</div>";
	return html;
}
