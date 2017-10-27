module('ObserverMenu', {
	mFileContent : null,
	setup : function() {
		this.mObsFactory = new ObserverFactoryMock();

		Singleton().setHttpTransportClass(HttpTransportStub);
		Singleton().setFactory(this.mObsFactory);
		Singleton().setActionClass(ActionImpl);
		Singleton().Transport().setSession("abc123");

		ObserverFactoryMock.NewObserver = new ObserverAcknowledgeNoParent();
		ObserverAuthentification.connectSetValue = this.setValue;
	},
	teardown : function() {
		ObserverAuthentification.connectSetValue = null;
		SingletonClose();
	},

});

test("Menu_Simple", function() {
	var json_receive = {
		"meta" : {
			observer : 'core.menu',
			source_extension : 'CORE',
			source_action : 'menu',
			text : 'Menu de l application'
		},
		"context" : {},
		"menus" : [ {
			"icon" : "/static/lucterios.CORE/images/general.png",
			"help" : "G\u00e9n\u00e9ralit\u00e9",
			"id" : "core.general",
			"menus" : [ {
				"params" : null,
				"icon" : "/static/lucterios.CORE/images/passwd.png",
				"help" : "Pour changer de mot de passe.",
				"id" : "CORE/changePassword",
				"unique" : "1",
				"modal" : "1",
				"text" : "Mot de passe",
				"action" : "changePassword",
				"extension" : "CORE",
				"close" : "1"
			} ],
			"unique" : "1",
			"modal" : "1",
			"text" : "G\u00e9n\u00e9ral",
			"params" : null,
			"close" : "1"
		}, {
			"icon" : "/static/lucterios.CORE/images/admin.png",
			"help" : "Gestion des r\u00e9glages et des configurations",
			"id" : "core.admin",
			"menus" : [ {
				"params" : null,
				"icon" : "/static/lucterios.CORE/images/config.png",
				"help" : "Afficher et modifier les param\u00e8tres principaux.",
				"id" : "CORE/configuration",
				"unique" : "1",
				"modal" : "1",
				"text" : "Configuration g\u00e9n\u00e9rale",
				"action" : "configuration",
				"extension" : "CORE",
				"close" : "1"
			}, {
				"icon" : "/static/lucterios.CORE/images/config_ext.png",
				"help" : "G\u00e9rer les configurations des modules",
				"id" : "core.extensions",
				"menus" : [ {
					"params" : null,
					"icon" : "/static/lucterios.CORE/images/config_search.png",
					"help" : "Liste de crit\u00e8res sauvegard\u00e9s pour les outils de recherche",
					"id" : "CORE/savedCriteriaList",
					"unique" : "1",
					"modal" : "0",
					"text" : "Crit\u00e8res sauvegard\u00e9s",
					"action" : "savedCriteriaList",
					"extension" : "CORE",
					"close" : "1"
				} ],
				"unique" : "1",
				"modal" : "1",
				"text" : "Modules (conf.)",
				"params" : null,
				"close" : "1"
			}, {
				"icon" : "/static/lucterios.CORE/images/permissions.png",
				"help" : "G\u00e9rer les utilisateurs, groupes et permissions.",
				"id" : "core.right",
				"menus" : [ {
					"params" : null,
					"icon" : "/static/lucterios.CORE/images/group.png",
					"help" : "G\u00e9rer les groupes.",
					"id" : "CORE/groupsList",
					"unique" : "1",
					"modal" : "0",
					"text" : "Les groupes",
					"action" : "groupsList",
					"extension" : "CORE",
					"close" : "1"
				}, {
					"params" : null,
					"icon" : "/static/lucterios.CORE/images/user.png",
					"help" : "G\u00e9rer les utilisateurs.",
					"id" : "CORE/usersList",
					"unique" : "1",
					"modal" : "0",
					"text" : "Utilisateurs",
					"action" : "usersList",
					"extension" : "CORE",
					"close" : "1"
				}, {
					"params" : null,
					"icon" : "/static/lucterios.CORE/images/session.png",
					"help" : "G\u00e9rer les sessions.",
					"id" : "CORE/sessionList",
					"unique" : "1",
					"modal" : "0",
					"text" : "Sessions",
					"action" : "sessionList",
					"extension" : "CORE",
					"close" : "1"
				} ],
				"unique" : "1",
				"modal" : "1",
				"text" : "Gestion des droits",
				"params" : null,
				"close" : "1"
			} ],
			"unique" : "1",
			"modal" : "1",
			"text" : "Administration",
			"params" : null,
			"close" : "1"
		} ]
	};
	var obs = new ObserverMenu();
	obs.setSource("CORE", "menu");
	obs.setContent(json_receive);
	obs.show("");

	equal(obs.menu_list.length, 2, "menu nb");
	equal(obs.menu_list[0].level, 0, '0:level');
	equal(obs.menu_list[0].icon, '/static/lucterios.CORE/images/general.png', '0:icon');
	equal(obs.menu_list[0].extension, '', '0:extension');
	equal(obs.menu_list[0].action, '', '0:action');
	equal(obs.menu_list[0].modal, '1', '0:modal');
	equal(obs.menu_list[0].help, 'Généralité', '0:help');
	equal(obs.menu_list[0].txt, 'Général', '0:txt');
	equal(obs.menu_list[0].submenu.length, 1, '0:icon');
	post_log(obs.menu_list[0].getHtml())

	var gui = obs.getGUI();
	ok(gui == null, "getGUI");

	var jcnt = $("#menuContainer");

	var lbl = jcnt.find("div:eq(0) > ul:eq(0) > li:eq(0) > a:eq(0)");
	equal(lbl.text(), 'Général', 'tab 1');
	var lbl = jcnt.find("div:eq(0) > ul:eq(0) > li:eq(1) > a:eq(0)");
	equal(lbl.text(), 'Administration', 'tab 2');

	var btn1 = jcnt.find("div:eq(0) > div:eq(0) > button:eq(0)");
	equal(btn1.text(), 'Mot de passePour changer de mot de passe.', 'btn 1');

	var btn2 = jcnt.find("div:eq(0) > div:eq(1) > button:eq(1)");
	equal(btn2.text(), 'Critères sauvegardésListe de critères sauvegardés pour les outils de recherche', 'btn 2');

	equal(this.mObsFactory.CallList.size(), 0, "Call Nb A");

	btn1.click();
	equal(this.mObsFactory.CallList.size(), 1, "Call Nb B");
	var expected_cmd = "CORE->changePassword()";
	equal(this.mObsFactory.CallList.get(0), expected_cmd, "Call #1");

	btn2.click();
	equal(this.mObsFactory.CallList.size(), 2, "Call Nb C");
	var expected_cmd = "CORE->savedCriteriaList()";
	equal(this.mObsFactory.CallList.get(1), expected_cmd, "Call #2");

	obs.close();
});

test("Menu_Status", function() {
	var json_receive = {
		meta : {
			observer : 'core.menu',
			source_extension : 'CORE',
			source_action : 'menu',
			text : 'Menu de l application'
		},
		"context" : {},
		menus : [ {
			"id" : "core.menu",
			"menus" : [ {
				"params" : null,
				"icon" : "/static/lucterios.CORE/images/status.png",
				"help" : "R\u00e9sum\u00e9",
				"id" : "CORE/statusMenu",
				"unique" : "1",
				"modal" : "1",
				"text" : "R\u00e9sum\u00e9",
				"action" : "statusMenu",
				"extension" : "CORE",
				"close" : "1"
			} ],
			"unique" : "1",
			"modal" : "1",
			"text" : "",
			"params" : null,
			"close" : "1"
		}, {
			"icon" : "/static/lucterios.CORE/images/general.png",
			"help" : "G\u00e9n\u00e9ralit\u00e9",
			"id" : "core.general",
			"menus" : [ {
				"params" : null,
				"icon" : "/static/lucterios.CORE/images/passwd.png",
				"help" : "Pour changer de mot de passe.",
				"id" : "CORE/changePassword",
				"unique" : "1",
				"modal" : "1",
				"text" : "Mot de passe",
				"action" : "changePassword",
				"extension" : "CORE",
				"close" : "1"
			} ],
			"unique" : "1",
			"modal" : "1",
			"text" : "G\u00e9n\u00e9ral",
			"params" : null,
			"close" : "1"
		} ]
	};

	var obs = new ObserverMenu();
	obs.setSource("CORE", "menu");
	obs.setContent(json_receive);
	obs.show("");

	var gui = obs.getGUI();
	ok(gui == null, "getGUI");

	var jcnt = $("#menuContainer");

	obs.close();
});
