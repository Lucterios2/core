/*global $,HashMap,ObserverAbstract, ObserverCustom,Class,Singleton, compBasic, GUIManage, createTable, createTab*/
/*global unusedVariables, createGuid, G_With_Extra_Menu*/

function resizeContentTabs() {
	var tabs_panel_height;
	if ($(window).width() > 1000) {
		$('#asideMenu').css('display', 'block');
		tabs_panel_height = $(window).height() - 130;
	} else if ($(window).width() > 623) {
		tabs_panel_height = $(window).height() - 180;
	} else {
		tabs_panel_height = $(window).height() - 130;
	}
	$(".ui-tabs-panel").css('max-height', tabs_panel_height + 'px');
	if ($(window).height() < 570) {
		$('.ui-accordion-content').css('height', (tabs_panel_height + 10) + 'px');
	}
	// post_log("{0}".format($(window).height()));
	// post_log("{0}".format($(window).width()));
}

function info_openclose() {
	var val_display = $("#asideMenu").css('display');
	if (val_display === 'none') {
		$("#asideMenu").css('display', 'block');
		$("#support").css('display', 'block');
		$("#menuContainer").removeClass("menupos");
		$("#asideMenu").accordion('option', 'active', 0);
	} else {
		$("#asideMenu").css('display', 'none');
		$("#support").css('display', 'none');
		$("#menuContainer").addClass("menupos");
	}
}

var Menu = Class.extend({

	id : '',
	shortcut : '',
	icon : '',
	extension : '',
	action : '',
	modal : '',
	help : '',
	txt : '',
	level : 0,

	submenu : null,
	rootHtml : '',
	act : null,

	obs : null,

	init : function(menu, level, owner) {
		this.level = level;
		this.submenu = [];

		this.id = menu.id.replace(/[_\.()'\`\/]/g, "");
		if (this.id !== "coremenu") {
			this.id += '_' + createGuid();
		}
		this.icon = menu.icon || '';
		this.extension = menu.extension || '';
		this.action = menu.action || '';
		this.modal = parseInt(menu.modal, 10) || 0;
		this.help = menu.help || '';
		this.txt = menu.text || '';

		if (this.action !== '') {
			this.act = Singleton().CreateAction();
			this.act.initialize(owner, Singleton().Factory(), menu);
			this.act.setClose(false);
		}
		if (menu.menus !== undefined) {
			var issMen, menu_item;
			for (issMen = 0; issMen < menu.menus.length; issMen++) {
				menu_item = new Menu(menu.menus[issMen], ++level, owner);
				if ((((menu_item.icon !== '') || G_With_Extra_Menu) && (menu_item.action !== null)) || (menu_item.submenu.length > 0)) {
					this.submenu.push(menu_item);
				}
			}
		}
	},

	getActFrame : function(itemType, style, is_root_level) {
		var html = '', default_style, submenu_idx;
		if ((this.icon !== '') || G_With_Extra_Menu) {
			html = '<{0} id="{1}" {2}>'.format(itemType, this.id, style);
			if (is_root_level === false) {
				if (this.icon !== "") {
					html += '<img src="{0}" />'.format(Singleton().Transport().getIconUrl(this.icon));
				}
				html += "<label><b>{0}</b></label>".format(this.txt);
			}
			if (this.help !== null && this.help !== "") {
				if (itemType === 'div') {
					html += '<span class="fa fa-question-circle" onclick="toggle_help(\'{0}\')"></span>'.format(this.id);
					default_style = 'display:none;';
				} else {
					default_style = 'display:line;';
				}
				html += "<div class='helper' style='{0}' >".format(default_style);
				html += "<label>{0}</label>".format(this.help.convertLuctoriosFormatToHtml());
				html += "</div>";
			}
			html += '</{0}>'.format(itemType);
		}
		for (submenu_idx = 0; submenu_idx < this.submenu.length; submenu_idx++) {
			html += this.submenu[submenu_idx].getHtml();
		}
		return html;
	},

	getHtml : function() {
		this.rootHtml = '';
		var html = "";
		// menu principal type dropdown sans action
		if (this.act === null) {
			// tabs de menu
			if (this.level === 0) {
				if (this.icon !== "") {
					this.rootHtml += '<img src="{0}" />'.format(Singleton().Transport().getIconUrl(this.icon));
				}
				this.rootHtml += "<span>{0}</span>".format(this.txt);
				html += this.getActFrame('div', "class='rootFrame'", true);
			} else {
				html += this.getActFrame('div', "class='menuFrame'", false);
			}
		} else {
			html += this.getActFrame('button', "", false);
		}
		return html;
	},

	addAction : function() {
		var act_function, comp, submenu_idx;
		if (this.obs !== null) {
			this.obs.show('');
			this.obs.refresh();
			act_function = function() {
				this.refresh();
			};
			comp = $("#title_{0}".format(this.obs.getId()));
			comp.click($.proxy(act_function, this.obs));
		} else if (this.act !== null) {
			act_function = function() {
				this.act.actionPerformed();
			};
			comp = $("#{0}".format(this.id));
			comp.click($.proxy(act_function, this));
		}
		for (submenu_idx = 0; submenu_idx < this.submenu.length; submenu_idx++) {
			this.submenu[submenu_idx].addAction();
		}
	}
});

var ObserverMenu = ObserverAbstract.extend({

	menu_json : null,
	menu_list : null,

	aside_menu : null,

	setContent : function(aJSON) {
		this._super(aJSON);
		this.menu_json = aJSON.menus;
		this.mRefresh = null;
	},

	getObserverName : function() {
		return "Core.Menu";
	},

	getParameters : function(aCheckNull) {
		unusedVariables(aCheckNull);
		var requete = new HashMap();
		requete.putAll(this.mContext);
		return requete;
	},

	setActive : function(aIsActive) {
		var submenu_idx, current_menu, bts;
		if (this.aside_menu) {
			for (submenu_idx = 0; submenu_idx < this.aside_menu.submenu.length; submenu_idx++) {
				current_menu = this.aside_menu.submenu[submenu_idx];
				current_menu.obs.setActive(aIsActive);
				$("#title_{0}".format(current_menu.txt)).prop("disabled", !aIsActive);
			}
		}
		bts = $("#menuContainer > div > div > button");
		bts.prop("disabled", !aIsActive);
	},

	closeEx : function() {
		$("#mainMenu").remove();
	},

	show : function(aTitle, aGUIType) {
		this._super(aTitle, aGUIType);
		this.setActive(true);

		this.aside_menu = null;
		var roothtml = [], html = [], iMen, menu_item, menu_idx;
		this.menu_list = [];
		for (iMen = 0; iMen < this.menu_json.length; iMen++) {
			menu_item = new Menu(this.menu_json[iMen], 0, this);
			if ((menu_item.id === "coremenu") && (menu_item.submenu.length > 0)) {
				this.aside_menu = menu_item;
			} else if (menu_item.submenu.length > 0) {
				html.push(menu_item.getHtml());
				roothtml.push(menu_item.rootHtml);
			}
			if (menu_item.submenu.length > 0) {
				this.menu_list.push(menu_item);
			}
		}
		$("#mainMenu").remove();
		$("#lucteriosClient").append("<div id='mainMenu' style='display:none;'/>");
		this.buildAsideMenu();
		html = '<div id="menuContainer">' + createTab(roothtml, html) + '</div>';
		$("#mainMenu").append(html);
		$(".tabContent").each(function() {
			$(this).tabs();
		});
		for (menu_idx = 0; menu_idx < this.menu_list.length; menu_idx++) {
			this.menu_list[menu_idx].addAction();
		}
		window.removeEventListener("resize", resizeContentTabs);
		resizeContentTabs();
		window.addEventListener("resize", resizeContentTabs);
		$("#mainMenu").css('display', 'block');
		if ((Singleton().mDesc !== null) && (Singleton().mDesc.mSupportHTML !== '')) {
			$("#mainMenu").append("<div id='support'>" + Singleton().mDesc.mSupportHTML.convertLuctoriosFormatToHtml() + '</div>');
		}
		if ((Singleton().mDesc !== null) && (!Singleton().mDesc.isCordovaVersionOk())) {
			$("#mainMenu").append("<div id='versionclient'>" + Singleton().getTranslate("Client obselete") + '</div>');
		}
		if (this.aside_menu === null) {
			$("#menuContainer").css('left', '0px');
			$("#support").css('display', 'none');
			$("#showmenu").css('display', 'none');
		}
		if (roothtml.length === 1) {
			$('ul[role="tablist"]').css('display', 'none');
		}
	},

	buildAsideMenu : function() {
		var html = '', submenu_idx, current_menu, menu_content, last_menu, size;
		if (this.aside_menu !== null) {
			html = '<div id="asideMenu" class="asideprop">';
			for (submenu_idx = 0; submenu_idx < this.aside_menu.submenu.length; submenu_idx++) {
				current_menu = this.aside_menu.submenu[submenu_idx];
				current_menu.obs = new ObserverCustom();
				current_menu.obs.setSource(current_menu.extension, current_menu.action);
				current_menu.obs.setContent({
					'context' : {},
					'comp' : {},
					'meta' : {},
					'data' : {}
				});
				current_menu.obs.mID = "aside_{0}".format(submenu_idx + 1);
				html += '<h3 id="title_{0}">{1}</h3>'.format(current_menu.obs.getId(), current_menu.txt);
				html += '<div id="{0}"></div>'.format(current_menu.obs.getId());
			}
			html += '</div>';
			$("#mainMenu").append(html);
			$("#asideMenu").accordion({
				collapsible : false,
				activate : function(event, ui) {
					unusedVariables(event, ui);
					var opened = $(this).find('.ui-state-active').length;
					if (opened === 0) {
						info_openclose();
					}
				}
			});
			size = 481 - this.aside_menu.submenu.length * 26;
			for (submenu_idx = 0; submenu_idx < this.aside_menu.submenu.length; submenu_idx++) {
				menu_content = $("#aside_{0}".format(submenu_idx + 1))[0];
				menu_content.style.height = size + 'px';
				menu_content.style.display = null;
			}
			last_menu = this.aside_menu.submenu[this.aside_menu.submenu.length - 1];
			$('#title_{0}'.format(last_menu.obs.getId())).click();
		}
		return html;
	}

});

var EmptyObserverMenu = ObserverMenu.extend({

	getObserverName : function() {
		return "Core.Menu";
	},

	show : function(aTitle, aGUIType) {
		unusedVariables(aTitle, aGUIType);
		$("#mainMenu").remove();
	}
});

function refreshCurrentAcideMenu() {
	var first = $('#asideMenu h3[aria-expanded="true"]:eq(0)'), acide_menu_id, title;
	if (first.length) {
		acide_menu_id = first.prop('id');
		if (acide_menu_id.substring(0, 6) !== 'title_') {
			acide_menu_id = 'title_' + acide_menu_id;
		}
		title = $('#' + acide_menu_id);
		title.click();
	}
}

function toggle_help(help_id) {
	var helper = $('#' + help_id + ' div.helper:eq(0)');
	if (helper.css('display') === 'none') {
		helper.css('display', 'block');
	} else {
		helper.css('display', 'none');
	}
}
