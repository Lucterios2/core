/*global $,HashMap,ObserverAbstract, ObserverCustom,Class,singleton, CompBasic, GUIManage, createTable, createTab, DIV_SUMMARY_TEMPLATE, SIDE_MENU_BUTTON_TEMPLATE*/
/*global unusedVariables, createGuid, G_With_Extra_Menu, CONTENT_MENU_BUTTON_TEMPLATE, ActionInt, CONTENT_MENU_INSIDE_PANEL_TEMPLATE, CONTENT_MENU_MAIN_DIV_TEMPLATE*/
'use strict';

var Menu = Class
    .extend({

        id: '',
        shortcut: '',
        icon: '',
        extension: '',
        action: '',
        modal: '',
        help: '',
        txt: '',
        level: 0,

        submenu: null,
        rootHtml: '',
        act: null,

        obs: null,

        init: function (menu, level, owner) {
            this.level = level;
            this.submenu = [];

            this.id = menu.getAttribute("id").replace(/[_\.()'\`\/]/g, "");
            if (this.id !== "coremenu") {
                this.id += '_' + createGuid();
            }
            this.shortcut = menu.getAttribute("shortcut");
            this.icon = menu.getAttribute("icon");
            if (this.icon === null) {
                this.icon = '';
            }
            this.extension = menu.getAttribute("extension");
            this.action = menu.getAttribute("action");
            this.modal = menu.getXMLAttributInt("modal", 0);
            this.help = menu.getCDataOfFirstTag('HELP')
                .convertLuctoriosFormatToHtml();
            this.txt = "";

            if (menu.hasChildNodes()) {
                this.txt = menu.firstChild.nodeValue;
            } else {
                this.txt = menu.text;
            }

            if (this.action !== null) {
                this.act = singleton().CreateAction();
                this.act.initialize(owner, singleton().Factory(), menu);
                this.act.setClose(false);
            }

            if (this.txt !== undefined && this.txt !== null && this.txt !== "") {
                this.txt = this.txt.replace(/_/, "");
            }

            var issMen, ssMenu, menu_item;
            for (issMen = 0; issMen < menu.childNodes.length; issMen += 1) {
                ssMenu = menu.childNodes[issMen];
                if (ssMenu.tagName === "MENU") {
                    level += 1;
                    menu_item = new Menu(ssMenu,  level, owner);
                    if ((((menu_item.icon !== '') || G_With_Extra_Menu) && (menu_item.action !== null)) || (menu_item.submenu.length > 0)) {
                        this.submenu.push(menu_item);
                    }
                }
            }
        },

        getActFrame: function (itemType, style) {
            var html = '',
                submenu_idx;
            if ((this.icon !== '') || G_With_Extra_Menu) {
                html = '<{0} id="{1}" {2}>'
                    .format(itemType, this.id, style);
                if (this.icon !== "") {
                    html += '<img src="{0}" />'.format(singleton()
                        .Transport().getIconUrl(this.icon));
                }
                html += "<span><b>{0}</b></span>".format(this.txt);
                if (this.help !== null && this.help !== "") {
                    html += "<br><font size='-2'>{0}</font>"
                        .format(this.help);
                }
                html += '</{0}>'.format(itemType);
            }
            for (submenu_idx = 0; submenu_idx < this.submenu.length; submenu_idx += 1) {
                html += this.submenu[submenu_idx].getHtml();
            }
            return html;
        },

        getHtml: function () {
            this.rootHtml = '';
            var html = "",
                submenu_idx;
            // menu principal type dropdown sans action
            if (this.action === null) {
                // tabs de menu
                if (this.level === 0) {
                    if (this.icon !== "") {
                        this.rootHtml += '<img src="{0}" />'
                            .format(singleton().Transport().getIconUrl(this.icon));
                    }
                    this.rootHtml += this.txt;
                    for (submenu_idx = 0; submenu_idx < this.submenu.length; submenu_idx += 1) {
                        html += this.submenu[submenu_idx].getHtml();
                    }
                } else {
                    // contenu
                    html += this.getActFrame('div', "class='menuFrame'");
                }
            } else {
                html += this.getActFrame('button', "");
            }
            return html;
        },

        addAction: function () {
            var act_function, comp, submenu_idx;
            if (this.obs !== null) {
                this.obs.show('');
                this.obs.refresh();
                act_function = function () {
                    this.refresh();
                };
                comp = $("#title_{0}".format(this.obs.getId()));
                comp.click($.proxy(act_function, this.obs));
            } else if (this.act !== null) {
                act_function = function () {
                    this.act.actionPerformed();
                };
                comp = $("#{0}".format(this.id));
                comp.click($.proxy(act_function, this));
            }
            for (submenu_idx = 0; submenu_idx < this.submenu.length; submenu_idx += 1) {
                this.submenu[submenu_idx].addAction();
            }
        }
    });

var ObserverMenu = ObserverAbstract
    .extend({

        menu_xml: null,
        menu_list: null,

        aside_menu: null,

        setContent: function (aDomXmlContent) {
            this._super(aDomXmlContent);
            this.menu_xml = this.mDomXmlContent
                .getElementsByTagName("MENUS")[0];
            this.mRefresh = null;
        },

        getObserverName: function () {
            return "Core.Menu";
        },

        getParameters: function (aCheckNull) {
            unusedVariables(aCheckNull);
            var requete = new HashMap();
            requete.putAll(this.mContext);
            return requete;
        },

        setActive: function (aIsActive) {
            var submenu_idx, current_menu, bts;
            if (this.aside_menu) {
                for (submenu_idx = 0; submenu_idx < this.aside_menu.submenu.length; submenu_idx += 1) {
                    current_menu = this.aside_menu.submenu[submenu_idx];
                    current_menu.obs.setActive(aIsActive);
                    $("#title_{0}".format(current_menu.txt)).prop("disabled", !aIsActive);
                }
            }
            bts = $("#menuContainer > div > div > button");
            bts.prop("disabled", !aIsActive);
        },

        closeEx: function () {
            $("#mainMenu").remove();
        },

        show: function (aTitle, aGUIType) {
            this._super(aTitle, aGUIType);
            this.setActive(true);

            this.aside_menu = null;
            var roothtml = [], html = [], iMen, menu, menu_item, menu_idx, main_menu, pos;
            this.menu_list = [];
            for (iMen = 0; iMen < this.menu_xml.childNodes.length; iMen += 1) {
                menu = this.menu_xml.childNodes[iMen];
                if (menu.tagName === "MENU") {
                    menu_item = new Menu(menu, 0, this);
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
            }
            $("#mainMenu").remove();
            $("#lucteriosClient").append("<div id='mainMenu' style='display:none;'/>");
            this.buildAsideMenu();
            html = '<div id="menuContainer">' + createTab(roothtml, html) + '</div>';
            $("#mainMenu").append(html);
            $(".tabContent").each(function () {
                $(this).tabs();
            });
            for (menu_idx = 0; menu_idx < this.menu_list.length; menu_idx += 1) {
                this.menu_list[menu_idx].addAction();
            }
            if (this.aside_menu !== null) {
                main_menu = $("#mainMenu");
                $("#mainMenu").split({
                    orientation: 'vertical',
                    limit: 0,
                    position: 300
                });
                $("#mainMenu").css('display', 'block');
                $("#mainMenu > div.vsplitter").dblclick(
                    function () {
                        main_menu = $("#mainMenu").split();
                        pos = $(this).position();
                        if (pos.left <= 5) {
                            main_menu.position(300, true);
                        } else {
                            main_menu.position(0, true);
                        }
                        main_menu.find('.splitter_panel').trigger('splitter.resize');
                    }
                );
            } else {
                $("#mainMenu").css('display', 'block');
            }
        },

        addMenuButton: function (menu, parent) {
            var html = CONTENT_MENU_BUTTON_TEMPLATE.format(
                menu.icon,
                menu.txt,
                menu.help,
                menu.id
            ), act, bt;
            $("#{0}".format(parent)).append(html);
            
            act = new ActionInt();
            act.initializeEx(menu, null, menu.txt, menu.extension, menu.action);
            
            bt = act.get_button();
            $("#BTCONTENT_{0}".format(menu.id)).on('click', bt.click);
        },

        addSubMenu: function (menus, parent) {
            var html = '', j, m2;
            for (j = 0; j < menus.length; j += 1) {
                m2 = menus[j];
                if (m2.action !== null) {
                    // build du bouton d'action
                    html = this.addMenuButton(m2, parent);
                } else {
                    // groupement d'actions
                    html = CONTENT_MENU_INSIDE_PANEL_TEMPLATE.format(
                        m2.id,
                        m2.icon,
                        m2.txt
                    );
                    $("#{0}".format(parent)).append(html);

                    if (m2.submenu.length > 0) {
                        this.addSubMenu(m2.submenu, "{0} > .panel-body".format(m2.id));
                    }
                }
            }
        },

        buildAsideMenu: function () {
            var html = '', submenu_idx, current_menu, size, active = '', i, m1, j;
            $("#mainmenucontent").html('');
            $("#mainsidemenu").html('');
            if (this.mAction === "menu") {
                // menu principal
                for (i = 0; i < this.menu_list.length; i += 1) {
                    m1 = this.menu_list[i];

                    if (m1.id === "coremenu") {
                        for (j = 0; j < m1.submenu.length; j += 1) {
                            if (this.action === "statusMenu") {
                                html = DIV_SUMMARY_TEMPLATE.format(
                                    this.txt,
                                    ''
                                );
                                $("#DIV_summary").html(html);
                            }
                        }
                    } else {
                        active = '';
                        if (i === 0) { active = " active"; }
                        html = SIDE_MENU_BUTTON_TEMPLATE.format(
                            active,
                            m1.id,
                            m1.icon,
                            m1.txt
                        );
                        $("#mainsidemenu").append(html);

                        // sous-menus dans un panel
                        html = CONTENT_MENU_MAIN_DIV_TEMPLATE.format(m1.id);
                        $("#mainmenucontent").append(html);

                        this.addSubMenu(m1.submenu, m1.id);
                    }
                }
            }

            $("button.lucterios-menu").click(function () {
                $("#navbar").toggleClass('visibleMenu');
            });
            $("a.switch-content").click(function () {
                $("div.content-container").hide();
                $("li.menu").removeClass("active");
                var divToShow = this.getAttribute("data");
                $("#" + divToShow).show();
                $(this).parent().addClass("active");
            });
        }

    });

function refreshCurrentAcideMenu() {
    var first = $('#asideMenu div[aria-expanded="true"]:eq(0)'), acide_menu_id, title;
    if (first.length) {
        acide_menu_id = first.prop('id');
        title = $('#title_' + acide_menu_id);
        title.click();
    }
}