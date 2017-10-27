module('ObserverFactoryRest', {
	setup : function() {
		Singleton().setActionClass(ActionImpl);
		ObserverStub.ObserverName = "ObserverStub";
		this.mHttpTransport = new HttpTransportStub();
		this.mObserverFactory = new ObserverFactoryRestImpl();
		this.mObserverFactory.setHttpTransport(this.mHttpTransport);
		this.mObserverFactory.clearObserverList();

		this.mObserverFactory.AddObserver("core.auth", ObserverStub);
		this.mObserverFactory.AddObserver("Core.Menu", ObserverStub);
		this.mObserverFactory.AddObserver("core.dialogbox", ObserverStub);
		this.mObserverFactory.AddObserver("core.custom", ObserverStub);
	},
	teardown : function() {
		this.mHttpTransport.close();
		this.mHttpTransport = null;
		SingletonClose();
	},
});

test("CallAction", function() {
	this.mHttpTransport.JSONReceive = {
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

	var current_params = new HashMap();
	var obs = this.mObserverFactory.callAction("lucterios.dummy", "multi", current_params, null);
	ok(obs != null, "Observer");
	equal(obs.getSourceAction(), "multi", "Action");
	equal(obs.getSourceExtension(), "lucterios.dummy", "Extension");
	equal(obs.getContext().size(), 3, "Context NB");
	equal(obs.getContext().get('personneMorale'), '100', "Context 1");
	equal(obs.getContext().get('CONFIRME'), "YES", "Context 2");
	equal(obs.getContext().get('bidule'), 'aaa', "Context 3");
	equal(obs.getTitle(), "Confirmation", "Titre");

	equal(this.mHttpTransport.XmlParam.size(), 1, 'XmlParam size');
	equal(this.mHttpTransport.XmlParam['WebFile'], "lucterios.dummy/multi", 'WebFile');
});

test("Refresh", function() {
	ObserverStub.ObserverName = "core.dialogbox";
	this.mHttpTransport.JSONReceive = {
		"context" : {
			'personneMorale' : '100',
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
			"title" : "Réinitialisation",
			"action" : "multi",
			"observer" : "core.dialogbox"
		}
	};

	var obs = new ObserverStub();
	obs.setSource("lucterios.dummy", "multi");
	obs.setContent(null);
	obs.mContext = new HashMap();
	obs.mContext.put("CONFIRME", "YES");

	this.mObserverFactory.callAction(obs.getSourceExtension(), obs.getSourceAction(), obs.getContext(), obs);

	equal(obs.getSourceAction(), "multi", "Action");
	equal(obs.getSourceExtension(), "lucterios.dummy", "Extension");
	equal(obs.getContext().size(), 2, "Context NB");
	equal(obs.getContext().get('personneMorale'), '100', "Context 2");
	equal(obs.getContext().get('bidule'), 'aaa', "Context 3");
	equal(obs.getTitle(), "Réinitialisation", "Titre");

	equal(this.mHttpTransport.XmlParam.size(), 2, 'XmlParam size');
	equal(this.mHttpTransport.XmlParam['WebFile'], "lucterios.dummy/multi", 'WebFile');
	equal(this.mHttpTransport.XmlParam['CONFIRME'], "YES", 'CONFIRME');
});

test("CallActionWithParam", function() {
	this.mHttpTransport.JSONReceive = {
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
			"title" : "Réinitialisation",
			"action" : "multi",
			"observer" : "core.dialogbox"
		}
	};

	var params = new HashMap();
	params.put("print_model", "107");
	params.put("CONFIRME", "YES");
	var obs = this.mObserverFactory.callAction("lucterios.dummy", "multi", params, null);
	equal(obs.getObserverName(), "ObserverStub", "Action");

	equal(this.mHttpTransport.XmlParam.size(), 3, 'XmlParam size');
	equal(this.mHttpTransport.XmlParam['WebFile'], "lucterios.dummy/multi", 'WebFile');
	equal(this.mHttpTransport.XmlParam['print_model'], "107", 'print_model');
	equal(this.mHttpTransport.XmlParam['CONFIRME'], "YES", 'CONFIRME');
});

test("CallActionBadXmlReceived", function() {
	this.mHttpTransport.XmlReceved = "Error php in truc.inc.php line 123";

	try {
		var obs = this.mObserverFactory.callAction("CORE", "printmodelReinit", new HashMap());
		ok(obs == null);
		ok(false);
	} catch (err) {
		equal(err.message, "Erreur inconnu");
		equal(err.toString(), "2~Erreur inconnu#CORE/printmodelReinit?");
	}
});

test("CallActionBadObserver", function() {
	this.mHttpTransport.JSONReceive = {
		"context" : {
			'personneMorale' : '100',
			'CONFIRME' : "YES",
			'bidule' : 'aaa',
		},
		"actions" : [],
		"close" : null,
		"data" : {
			"text" : "Do you want?",
			"type" : 2
		},
		"meta" : {
			"extension" : "lucterios.dummy",
			"title" : "Réinitialisation",
			"action" : "multi",
			"observer" : "core.dialbox"
		}
	};

	try {
		var obs = this.mObserverFactory.callAction("lucterios.dummy", "multi", new HashMap());
		ok(obs == null);
		ok(false);
	} catch (err) {
		equal(err.message, "Observeur 'core.dialbox' inconnu.");
		equal(err.toString().substring(0, 70), "3~Observeur 'core.dialbox' inconnu.#lucterios.dummy/multi?#{\"context\":");
	}
});

test("Authentification", function() {
	ObserverStub.ObserverName = "core.auth";

	this.mHttpTransport.JSONReceive = {
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
	ok(!this.mObserverFactory.setAuthentification("abc", "123"), "Bad");
	equal(this.mHttpTransport.getSession(), "", "Session Bad");

	equal(this.mHttpTransport.XmlParam.size(), 3, 'XmlParam size');
	equal(this.mHttpTransport.XmlParam['WebFile'], "CORE/authentification", 'WebFile');
	equal(this.mHttpTransport.XmlParam["username"], "abc", "username");
	equal(this.mHttpTransport.XmlParam["password"], "123", "password");

	this.mHttpTransport.JSONReceive = {
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
	ok(this.mObserverFactory.setAuthentification("admin", "admin"), "auth OK");
	equal(this.mHttpTransport.getSession(), "admin1315821586", "Session OK");

	equal(this.mHttpTransport.XmlParam.size(), 3, 'XmlParam size');
	equal(this.mHttpTransport.XmlParam['WebFile'], "CORE/authentification", 'WebFile');
	equal(this.mHttpTransport.XmlParam["username"], "admin", "username");
	equal(this.mHttpTransport.XmlParam["password"], "admin", "password");
});
