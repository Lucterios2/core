module('Observer', {
	mFileContent : null,
	mCalled : 0,

	setup : function() {
		this.mObsFactory = new ObserverFactoryMock();

		Singleton().setHttpTransportClass(HttpTransportStub);
		Singleton().setFactory(this.mObsFactory);
		Singleton().setActionClass(ActionImpl);
		Singleton().Transport().setSession("abc123");
		Singleton().Transport().setLastLogin("admin");
		Singleton().mSelectLang = 'fr';
		this.mObsFactory.setHttpTransport(Singleton().Transport());

		ObserverFactoryMock.NewObserver = new ObserverAcknowledge();
		ObserverAuthentification.connectSetValue = this.setValue;
		g_InitialCallBack = $.proxy(this.callback, this);
	},

	teardown : function() {
		ObserverAuthentification.connectSetValue = null;
		g_InitialCallBack = null;
		SingletonClose();
	},

	saveFile : function(aContent, aFileName) {
		this.mFileContent = atob(aContent);
		this.mFileName = aFileName;
	},

	callback : function() {
		this.mCalled++;
	}

});

test(
		"Authentification 1",
		function() {
			Singleton().Transport().setSession("");
			var json_receive = {
				"connexion" : {
					"SUPPORT_EMAIL" : "support@lucterios.org",
					"VERSION" : "2.1.1.16062115",
					"SERVERVERSION" : "2.1.15.17102417",
					"REALNAME" : "Administrateur ",
					"COPYRIGHT" : "(c) 2015 lucterios.org - GPL Licence",
					"MODE" : "0",
					"LOGIN" : "admin",
					"LOGONAME" : "http://demo.lucterios.org/Lucterios/extensions/applis/images/logo.gif",
					"LANGUAGE" : "fr",
					"INSTANCE" : "dev",
					"SUPPORT_HTML" : "",
					"INFO_SERVER" : [ "C\u0153ur Lucterios=2.1.15.17102417", "Lucterios standard=2.1.1.16062115", "",
							"{[i]}Linux x86_64 3.19.0-32-generic - Python 3.4.3 - Django 1.10.4{[/i]}" ],
					"SUBTITLE" : "Application g\u00e9n\u00e9rique de gestion",
					"TITLE" : "Lucterios standard",
					"EMAIL" : "Support Lucterios <support@lucterios.org>",
					"BACKGROUND" : ""
				},
				"close" : null,
				"context" : {
					"username" : "admin",
					"ses" : "admin1315821586",
					"password" : "admin"
				},
				"data" : "OK",
				"meta" : {
					"title" : "info",
					"action" : "authentification",
					"observer" : "core.auth",
					"extension" : "CORE"
				}
			};

			var obs = new ObserverAuthentification();
			obs.setSource("CORE", "Auth");
			obs.setContent(json_receive);
			obs.show("Mon titre");

			equal(obs.getGUI(), null, "getGUI");

			var description = Singleton().mDesc;
			equal(description.getTitle(), "Lucterios standard", "Title");
			equal(description.getApplisVersion(), "2.1.1.16062115", "ApplisVersion");
			equal(description.getServerVersion(), "2.1.15.17102417", "ServerVersion");
			equal(description.getCopyRigth(), "(c) 2015 lucterios.org - GPL Licence", "CopyRigth");
			equal(description.getLogoIconName(), "http://demo.lucterios.org/Lucterios/extensions/applis/images/logo.gif", "LogoIconName");
			equal(
					description.getInfoServer(),
					"Cœur Lucterios=2.1.15.17102417{[br/]}Lucterios standard=2.1.1.16062115{[br/]}{[br/]}{[i]}Linux x86_64 3.19.0-32-generic - Python 3.4.3 - Django 1.10.4{[/i]}",
					"InfoServer");
			equal(description.getSupportEmail(), "Support Lucterios <support@lucterios.org>", "SupportEmail");

			equal(description.getSubTitle(), "Application générique de gestion", "SubTitle");
			equal(description.getLogin(), "admin", "Login");
			equal(description.getRealName(), "Administrateur", "RealName");
			equal(Singleton().mRefreshMenu, true, "RefreshMenu");
			equal(obs.getRefreshMenu(), false, "RefreshMenu obs");
			equal(Singleton().Transport().getSession(), 'admin1315821586', "session");
		});

test("Authentification 2", function() {
	var json_receive = {
		"close" : null,
		"context" : {
			"username" : "admin",
			"password" : "abc123"
		},
		"actions" : [ {
			"unique" : "1",
			"icon" : "/static/lucterios.CORE/images/passwd.png",
			"action" : "askPassword",
			"close" : "0",
			"extension" : "CORE",
			"text" : "Mot de passe ou alias oubli\u00e9?",
			"params" : null,
			"id" : "CORE/askPassword",
			"modal" : "1"
		} ],
		"data" : "BADAUTH",
		"meta" : {
			"title" : "info",
			"action" : "authentification",
			"observer" : "core.auth",
			"extension" : "CORE"
		}
	};

	var obs = new ObserverAuthentification();
	obs.setSource('CORE', "authentification");
	obs.setContent(json_receive);
	obs.show("Connexion");

	var gui = obs.getGUI();
	ok(gui != null, "getGUI");
	ok(gui.isExist(), "GUI exist");

	var jcnt = gui.getHtmlDom();

	var lbl = jcnt.find("table:eq(0) > tbody > tr:eq(0) > td:eq(0) > label");
	equal(lbl.text(), "Alias ou Mot de passe incorrect!", 'text 1');

	var lbl = jcnt.find("table:eq(0) > tbody > tr:eq(1) > td:eq(0) > span");
	equal(lbl.html(), "<b>Alias</b>", 'text 2');

	var lbl = jcnt.find("table:eq(0) > tbody > tr:eq(1) > td:eq(1) > input");
	equal(lbl.val(), "", 'alias');
	lbl.val('machin')

	var lbl = jcnt.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0) > span");
	equal(lbl.html(), "<b>Mot de passe</b>", 'text 3');

	var lbl = jcnt.find("table:eq(0) > tbody > tr:eq(2) > td:eq(1) > input");
	equal(lbl.val(), "", 'MdP');
	lbl.val('coucou')

	var btn1 = jcnt.parent().find("div:eq(2) > div:eq(0) > button:eq(0)");
	equal(btn1.text(), 'Ok', 'btn 1');
	var btn2 = jcnt.parent().find("div:eq(2) > div:eq(0) > button:eq(1)");
	equal(btn2.text(), 'Annuler', 'btn 2');

	equal(this.mObsFactory.CallList.size(), 0, "Call A Nb");

	btn1.click();

	ok(!gui.isExist(), "GUI exist again");
	equal(this.mObsFactory.CallList.size(), 1, "Call B Nb");
	equal(this.mObsFactory.CallList.get(0), "CORE->authentification(username='machin',password='coucou',)", "Call #1");
});

test("Authentification 3", function() {
	var json_receive = {
		"close" : null,
		"context" : {},
		"data" : "NEEDAUTH",
		"meta" : {
			"title" : "info",
			"action" : "authentification",
			"observer" : "core.auth",
			"extension" : "CORE"
		}
	};
	equal(this.mCalled, 0, "Initial");

	var obs = new ObserverAuthentification();
	obs.setSource('CORE', "authentification");
	obs.setContent(json_receive);
	obs.show("Connexion");

	equal(this.mCalled, 1, "Begin");
	
	var gui = obs.getGUI();
	ok(gui != null, "getGUI");
	ok(gui.isExist(), "GUI exist");

	var jcnt = gui.getHtmlDom();

	var lbl = jcnt.find("table:eq(0) > tbody > tr:eq(0) > td:eq(0) > label");
	equal(lbl.text(), "Veuillez vous identifier", 'text 1');

	var btn1 = jcnt.parent().find("div:eq(2) > div:eq(0) > button:eq(0)");
	equal(btn1.text(), 'Ok', 'btn 1');
	var btn2 = jcnt.parent().find("div:eq(2) > div:eq(0) > button:eq(1)");
	equal(btn2.text(), 'Annuler', 'btn 2');

	Singleton().mDesc = 0;
	equal(this.mObsFactory.CallList.size(), 0, "Call A Nb");
	equal(this.mCalled, 1, "Called A");

	btn2.click();

	ok(!gui.isExist(), "GUI exist again");
	equal(this.mObsFactory.CallList.size(), 0, "Call B Nb");

	equal(this.mCalled, 2, "Called B");
	equal(Singleton().mDesc, null, 'Desc null');
});

test("Acknowledge", function() {
	var json_receive = {
		"close" : {
			"params" : null,
			"id" : "CORE/unlock",
			"unique" : "1",
			"modal" : "1",
			"text" : "unlock",
			"action" : "unlock",
			"extension" : "CORE",
			"close" : "1"
		},
		"action" : {
			"params" : null,
			"id" : "toto/bidule",
			"unique" : "1",
			"modal" : "1",
			"text" : "",
			"action" : "bidule",
			"extension" : "toto",
			"close" : "1"
		},
		"context" : {
			"LOCK_IDENT" : "lucterios.CORE.models-LucteriosGroup-1",
			"group" : "1"
		},
		"meta" : {
			"title" : "",
			"action" : "groupsEdit",
			"observer" : "core.acknowledge",
			"extension" : "CORE"
		}
	};

	var obs = new ObserverAcknowledge();
	obs.setSource("CORE", "groupsEdit");
	obs.setContent(json_receive);
	obs.show("Mon titre");

	ok(obs.getGUI() == null, "getGUI");

	equal(obs.getContext().size(), 2, "Context size");
	equal(obs.getContext().get("group"), "1", "Context 1");

	ok(obs.getRedirectAction() != null, "RedirectAction");
	equal(obs.getRedirectAction().getExtension(), "toto", "RedirectAction-Extension");
	equal(obs.getRedirectAction().getAction(), "bidule", "RedirectAction-Action");

	equal(this.mObsFactory.CallList.size(), 2, "Call Nb");
	equal(this.mObsFactory.CallList.get(0), "CORE->unlock(LOCK_IDENT='lucterios.CORE.models-LucteriosGroup-1',group='1',)", "Call #1");
	equal(this.mObsFactory.CallList.get(1), "toto->bidule(LOCK_IDENT='lucterios.CORE.models-LucteriosGroup-1',group='1',)", "Call #2");
});

test(
		"Exception1",
		function() {
			Singleton().mDesc = new ApplicationDescription("aa", "bb", "cc", "dd", "ee");
			var json_receive = {
				"context" : {},
				"close" : null,
				"exception" : {
					"message" : "Critique",
					"debug" : "/usr/local/lib/python3.4/site-packages/django/views/generic/base.py in line 88 in dispatch : return handler(request, *args, **kwargs){[br/]}/home/dev/Lucterios2/lct-core/lucterios/framework/xferbasic.py in line 332 in get : return self.get_post(request, *args, **kwargs){[br/]}/home/dev/Lucterios2/lct-core/lucterios/framework/xfergraphic.py in line 159 in get_post : self.fillresponse(**self._get_params()){[br/]}/home/dev/Lucterios2/lct-core/lucterios/dummy/views.py in line 55 in fillresponse : raise LucteriosException(GRAVE, \"Error of bidule\"){[br/]}",
					"code" : "1",
					"type" : "LucteriosException"
				},
				"meta" : {
					"extension" : "lucterios.dummy",
					"title" : "",
					"action" : "bidule",
					"observer" : "core.exception"
				}
			};

			var obs = new ObserverException();
			obs.setSource("CORE", "validerAct");
			obs.setContent(json_receive);
			obs.show("Mon titre");

			var gui = obs.getGUI();
			ok(gui != null, "getGUI");
			ok(gui.isExist(), "GUI exist");

			var jcnt = gui.getHtmlDom();
			var img = jcnt.find("table:eq(0) > tbody > tr:eq(0) > td:eq(0) > img");
			equal(img.attr('src').substr(-9), 'error.png', "image");

			var lbl = jcnt.find("table:eq(0) > tbody > tr:eq(0) > td:eq(1) > label");
			equal(lbl.text(), 'Critique', 'text');

			var btn1 = jcnt.find("table:eq(0) > tbody > tr:eq(1) > td:eq(0) > input[name='info']");
			equal(btn1.attr('value'), '>>', 'btn 1');
			equal(btn1.attr('type'), 'button', 'btn 1');
			var btn2 = jcnt.find("table:eq(0) > tbody > tr:eq(1) > td:eq(0) > input[name='send']");
			equal(btn2.attr('value'), 'Envoyer au support', 'btn 2');
			equal(btn2.attr('type'), 'button', 'btn 2');

			var memo = jcnt.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0) > div > div > pre");
			equal(
					memo.text(),
					"/usr/local/lib/python3.4/site-packages/django/views/generic/base.py in line 88 in dispatch : return handler(request, *args, **kwargs)\n"
							+ "/home/dev/Lucterios2/lct-core/lucterios/framework/xferbasic.py in line 332 in get : return self.get_post(request, *args, **kwargs)\n"
							+ "/home/dev/Lucterios2/lct-core/lucterios/framework/xfergraphic.py in line 159 in get_post : self.fillresponse(**self._get_params())\n"
							+ "/home/dev/Lucterios2/lct-core/lucterios/dummy/views.py in line 55 in fillresponse : raise LucteriosException(GRAVE, \"Error of bidule\")",
					"stack");

			var lbl = jcnt.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0) > div > div > label");
			equal(lbl.text(), 'LucteriosException', 'extra');

			equal(this.mObsFactory.CallList.size(), 0, "Call Nb");
			gui.close();
			ok(!gui.isExist(), "GUI remove");
		});

test(
		"Exception2",
		function() {
			var json_receive = {
				"exception" : {
					"type" : "LucteriosException",
					"debug" : "/usr/local/lib/python3.4/site-packages/django/views/generic/base.py in line 88 in dispatch : return handler(request, *args, **kwargs){[br/]}/home/dev/Lucterios2/lct-core/lucterios/framework/xferbasic.py in line 332 in get : return self.get_post(request, *args, **kwargs){[br/]}/home/dev/Lucterios2/lct-core/lucterios/framework/xferadvance.py in line 162 in get_post : self._initialize(request, *args, **kwargs){[br/]}/home/dev/Lucterios2/lct-core/lucterios/framework/xferbasic.py in line 260 in _initialize : self._search_model(){[br/]}/home/dev/Lucterios2/lct-core/lucterios/framework/xferbasic.py in line 172 in _search_model : self._load_unique_record(ids[0]){[br/]}/home/dev/Lucterios2/lct-core/lucterios/framework/xferbasic.py in line 160 in _load_unique_record : IMPORTANT, _(\"This record not exist!\\nRefresh your application.\")){[br/]}",
					"message" : "Mineur",
					"code" : "4"
				},
				"close" : null,
				"context" : {
					"username" : "admin",
					"group" : "50",
					"password" : "adms"
				},
				"meta" : {
					"title" : "",
					"action" : "groupsEdit",
					"observer" : "core.exception",
					"extension" : "CORE"
				}
			};

			var obs = new ObserverException();
			obs.setSource("CORE", "groupsEdit");
			obs.setContent(json_receive);
			obs.show("Mon titre");

			var gui = obs.getGUI();
			ok(gui != null, "getGUI");
			ok(gui.isExist(), "GUI exist");

			var jcnt = gui.getHtmlDom();
			var img = jcnt.find("table > tbody > tr:eq(0) > td:eq(0) > img");
			equal(img.attr('src').substr(-8), 'info.png', "image");

			var lbl = jcnt.find("table > tbody > tr:eq(0) > td:eq(1) > label");
			equal(lbl.text(), 'Mineur', 'text');

			var btn1 = jcnt.find("table:eq(0) > tbody > tr:eq(1) > td:eq(0) > input");
			equal(btn1.length, 0, 'no btn 1');
			var btn2 = jcnt.find("table:eq(0) > tbody > tr:eq(1) > td:eq(1) > input");
			equal(btn2.length, 0, 'no btn 2');

			var memo = jcnt.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0) > div > div > pre");
			equal(memo.length, 0, "no stack");

			var lbl = jcnt.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0) > div > div > label");
			equal(lbl.length, 0, 'no extra');

			equal(this.mObsFactory.CallList.size(), 0, "Call Nb");
			gui.close();
			ok(!gui.isExist(), "GUI remove");
		});

test(
		"Print",
		function() {
			var json_receive = {
				"context" : {
					"PRINT_MODE" : "4",
					"example" : "1"
				},
				"close" : null,
				"print" : {
					"title" : "Example d'impression",
					"mode" : 4,
					"content" : "CiAgICAgICJFeGFtcGxlIgogICAgCiAgICAgIAogICAgICAibmFtZSIKICAgICAgImFhYWEiCiAgICAgICJ2YWx1ZSIKICAgICAgIjUiCiAgICAgICJwcmljZSIKICAgICAgIjEwMC4wMCIKICAgICAgImRhdGUiCiAgICAgICItLS0iCiAgICAgICJ0aW1lIgogICAgICAiMDA6MDAiCiAgICAgICJ2YWxpZCIKICAgICAgIk5vbiIKICAgICAgImNvbW1lbnQiCiAgICAgICJxcXFxIgogICAgCg=="
				},
				"meta" : {
					"extension" : "lucterios.dummy",
					"title" : "Example d'impression",
					"action" : "examplePrint",
					"observer" : "core.print"
				}
			};

			Singleton().mFileManager = this;
			equal(this.mFileContent, null, "Empty file");
			var obs = new ObserverPrint();
			obs.setSource("lucterios.dummy", "examplePrint");
			obs.setContent(json_receive);
			obs.show("Example d'impression");

			equal(obs.getContext().size(), 2, "Context size");
			equal(obs.getContext().get("example"), "1", "Context 1");
			equal(obs.getContext().get("PRINT_MODE"), "4", "Context 2");
			equal(obs.mode, MODE_EXPORT_CSV, 'mode');
			equal(obs.title, "Example d'impression", 'title');

			ok(this.mFileContent != null, "File write");
			var contents = this.mFileContent.split('\n');
			post_log(contents);
			equal(contents.length, 20, "File size");
			equal(contents[1].trim(), "\"Example\"", "title");
			equal(contents[4].trim(), "\"name\"", "header");
			equal(contents[6].trim(), "\"value\"", "line #2");
			equal(this.mFileName, 'Example_d_impression.csv', 'file name');
			equal(this.mObsFactory.CallList.size(), 0, "Call Nb");
		});

test("Dialog", function() {
	var json_receive = {
		"context" : {
			'personneMorale' : '100',
			'CONFIRME' : "YES",
			'bidule' : 'aaa',
		},
		"actions" : [ {
			"params" : {
				"CONFIRME" : "YES"
			},
			"icon" : "/static/lucterios.CORE/images/ok.png",
			"close" : "0",
			"unique" : "1",
			"extension" : "lucterios.dummy",
			"text" : "Oui",
			"modal" : "1",
			"id" : "lucterios.dummy/multi",
			"action" : "multi"
		}, {
			"unique" : "1",
			"id" : "",
			"close" : "1",
			"icon" : "/static/lucterios.CORE/images/cancel.png",
			"text" : "Non",
			"modal" : "1",
			"params" : null
		} ],
		"close" : null,
		"data" : {
			"text" : "Do you want?",
			"type" : 2
		},
		"meta" : {
			"extension" : "lucterios.dummy",
			"title" : "Confirmation",
			"action" : "multi",
			"observer" : "core.dialogbox"
		}
	};

	var obs = new ObserverDialogBox();
	obs.setSource("lucterios.dummy", "multi");
	obs.setContent(json_receive);
	obs.show("multi");

	var gui = obs.getGUI();
	ok(gui != null, "getGUI");
	ok(gui.isExist(), "GUI exist");

	var jcnt = gui.getHtmlDom();
	var img = jcnt.find("table:eq(0) > tbody > tr:eq(0) > td:eq(0) > img");
	equal(img.attr('src').substr(-11), 'confirm.png', "image");

	var lbl = jcnt.find("table:eq(0) > tbody > tr:eq(0) > td:eq(1) > label");
	equal(lbl.text(), "Do you want?", 'text');

	var btn1 = jcnt.parent().find("div:eq(2) > div:eq(0) > button:eq(0)");
	equal(btn1.text(), 'Oui', 'btn 1');
	var btn2 = jcnt.parent().find("div:eq(2) > div:eq(0) > button:eq(1)");
	equal(btn2.text(), 'Non', 'btn 2');

	equal(obs.getContext().size(), 3, "Context size");
	equal(obs.getContext().get("personneMorale"), "100", "Context 1");
	equal(obs.getContext().get("CONFIRME"), "YES", "Context 2");

	equal(this.mObsFactory.CallList.size(), 0, "Call A Nb");

	btn1.click();

	ok(gui.isExist(), "GUI exist again");
	equal(this.mObsFactory.CallList.size(), 2, "Call B Nb");
	equal(this.mObsFactory.CallList.get(0), "lucterios.dummy->multi(personneMorale='100',CONFIRME='YES',bidule='aaa',)", "Call #1");
	equal(this.mObsFactory.CallList.get(1), "lucterios.dummy->multi(personneMorale='100',CONFIRME='YES',bidule='aaa',)", "Call #2");

	btn2.click();
	ok(!gui.isExist(), "GUI close");
	equal(this.mObsFactory.CallList.size(), 2, "Call C Nb :" + this.mObsFactory.CallList.toString());
});
