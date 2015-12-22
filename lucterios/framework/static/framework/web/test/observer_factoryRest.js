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

test(
		"CallAction",
		function() {
			this.mHttpTransport.XmlReceved = "<REPONSES><REPONSE observer='core.dialogbox' source_extension='CORE' source_action='printmodelReinit'><CONTEXT><PARAM name='print_model'><![CDATA[107]]></PARAM><PARAM name='CONFIRME'><![CDATA[YES]]></PARAM></CONTEXT><TITLE>Réinitialisation de modele</TITLE><TEXT type='2'><![CDATA[Etes-vous sure de reinitialiser ce modele?]]></TEXT><ACTIONS><ACTION action='printmodelReinit' extension='CORE' icon='images/ok.png'><![CDATA[Oui]]></ACTION><ACTION icon='images/cancel.png'><![CDATA[Non]]></ACTION></ACTIONS></REPONSE></REPONSES>";

			var current_params = new HashMap();
			var obs = this.mObserverFactory.callAction("CORE",
					"printmodelReinit", current_params, null);
			ok(obs != null, "Observer");
			equal(obs.getSourceAction(), "printmodelReinit", "Action");
			equal(obs.getSourceExtension(), "CORE", "Extension");
			equal(obs.getContext().size(), 2, "Context NB");
			equal(obs.getContext()["print_model"], "107", "Context 1");
			equal(obs.getContext()["CONFIRME"], "YES", "Context 2");
			equal(
					obs.getContentText(),
					'<TITLE>Réinitialisation de modele</TITLE><TEXT type="2"><![CDATA[Etes-vous sure de reinitialiser ce modele?]]></TEXT><ACTIONS><ACTION action="printmodelReinit" extension="CORE" icon="images/ok.png"><![CDATA[Oui]]></ACTION><ACTION icon="images/cancel.png"><![CDATA[Non]]></ACTION></ACTIONS>',
					"Content");

			equal(obs.getTitle(), "Réinitialisation de modele", "Titre");

			equal(this.mHttpTransport.XmlParam.size(), 1, 'XmlParam size');
			equal(this.mHttpTransport.XmlParam['WebFile'],
					"CORE/printmodelReinit", 'WebFile');
		});

test(
		"Refresh",
		function() {
			ObserverStub.ObserverName = "core.dialogbox";
			this.mHttpTransport.XmlReceved = "<?xml version='1.0' encoding='ISO-8859-1'?><REPONSES><REPONSE observer='core.dialogbox' source_extension='CORE' source_action='printmodelReinit'><CONTEXT><PARAM name='print_model'><![CDATA[107]]></PARAM><PARAM name='CONFIRME'><![CDATA[YES]]></PARAM></CONTEXT><TITLE>Réinitialisation</TITLE><TEXT type='2'><![CDATA[Etes-vous sure de reinitialiser ce modele?]]></TEXT><ACTIONS><ACTION icon='images/ok.png' extension='CORE' action='printmodelReinit'><![CDATA[Oui]]></ACTION><ACTION icon='images/cancel.png'><![CDATA[Non]]></ACTION></ACTIONS></REPONSE></REPONSES>";

			var obs = new ObserverStub();
			obs.setSource("CORE", "printmodelReinit");
			obs.setContent(null);
			obs.mContext = new HashMap();
			obs.mContext.put("print_model", "107");
			obs.mContext.put("CONFIRME", "YES");

			this.mObserverFactory.callAction(obs.getSourceExtension(), obs
					.getSourceAction(), obs.getContext(), obs);

			equal(obs.getSourceAction(), "printmodelReinit", "Action");
			equal(obs.getSourceExtension(), "CORE", "Extension");
			equal(obs.getContext().size(), 2, "Context NB");
			equal(obs.getContext().get("print_model"), "107", "Context 1");
			equal(obs.getContext().get("CONFIRME"), "YES", "Context 2");
			equal(
					obs.getContentText(),
					'<TITLE>Réinitialisation</TITLE><TEXT type="2"><![CDATA[Etes-vous sure de reinitialiser ce modele?]]></TEXT><ACTIONS><ACTION icon="images/ok.png" extension="CORE" action="printmodelReinit"><![CDATA[Oui]]></ACTION><ACTION icon="images/cancel.png"><![CDATA[Non]]></ACTION></ACTIONS>',
					"Content");
			equal(obs.getTitle(), "Réinitialisation", "Titre");

			equal(this.mHttpTransport.XmlParam.size(), 3, 'XmlParam size');
			equal(this.mHttpTransport.XmlParam['WebFile'],
					"CORE/printmodelReinit", 'WebFile');
			equal(this.mHttpTransport.XmlParam['print_model'], "107",
					'print_model');
			equal(this.mHttpTransport.XmlParam['CONFIRME'], "YES", 'CONFIRME');
		});

test(
		"CallActionWithParam",
		function() {
			this.mHttpTransport.XmlReceved = "<?xml version='1.0' encoding='ISO-8859-1'?><REPONSES><REPONSE observer='core.dialogbox' source_extension='CORE' source_action='printmodelReinit'><CONTEXT><PARAM name='print_model'><![CDATA[107]]></PARAM><PARAM name='CONFIRME'><![CDATA[YES]]></PARAM></CONTEXT><TEXT type='2'><![CDATA[Etes-vous sure de reinitialiser ce modele?]]></TEXT><ACTIONS><ACTION icon='images/ok.png' extension='CORE' action='printmodelReinit'><![CDATA[Oui]]></ACTION><ACTION icon='images/cancel.png'><![CDATA[Non]]></ACTION></ACTIONS></REPONSE></REPONSES>";

			var params = new HashMap();
			params.put("print_model", "107");
			params.put("CONFIRME", "YES");
			var obs = this.mObserverFactory.callAction("CORE",
					"printmodelReinit", params, null);
			equal(obs.getObserverName(), "ObserverStub", "Action");

			equal(this.mHttpTransport.XmlParam.size(), 3, 'XmlParam size');
			equal(this.mHttpTransport.XmlParam['WebFile'],
					"CORE/printmodelReinit", 'WebFile');
			equal(this.mHttpTransport.XmlParam['print_model'], "107",
					'print_model');
			equal(this.mHttpTransport.XmlParam['CONFIRME'], "YES", 'CONFIRME');
		});

test(
		"CallActionBadXmlReceived",
		function() {
			this.mHttpTransport.XmlReceved = "Error php in truc.inc.php line 123";

			try {
				var obs = this.mObserverFactory.callAction("CORE",
						"printmodelReinit", new HashMap());
				ok(obs == null);
				ok(false);
			} catch (err) {
				equal(err.message, "Erreur de parsing xml");
				equal(
						err.toString().substring(0, 86),
						"2~Erreur de parsing xml#CORE/printmodelReinit?#Error php in truc.inc.php line 123\nMsg:");
			}
		});

test(
		"CallActionBadObserver",
		function() {
			this.mHttpTransport.XmlReceved = "<?xml version='1.0' encoding='ISO-8859-1'?><REPONSES><REPONSE observer='Core.BialogDox' source_extension='CORE' source_action='printmodelReinit'><CONTEXT><PARAM name='print_model'><![CDATA[107]]></PARAM><PARAM name='CONFIRME'><![CDATA[YES]]></PARAM></CONTEXT><TEXT type='2'><![CDATA[Etes-vous sure de reinitialiser ce modele?]]></TEXT><ACTIONS><ACTION icon='images/ok.png' extension='CORE' action='printmodelReinit'><![CDATA[Oui]]></ACTION><ACTION icon='images/cancel.png'><![CDATA[Non]]></ACTION></ACTIONS></REPONSE></REPONSES>";

			try {
				var obs = this.mObserverFactory.callAction("CORE",
						"printmodelReinit", new HashMap());
				ok(obs == null);
				ok(false);
			} catch (err) {
				equal(
						err.message,
						"Observeur 'Core.BialogDox' inconnu{[newline]}Veuillez utiliser le client Java.");
				equal(
						err.toString().substring(0, 192),
						"3~Observeur 'Core.BialogDox' inconnu{[newline]}Veuillez utiliser le client Java.#CORE/printmodelReinit?#<?xml version='1.0' encoding='ISO-8859-1'?><REPONSES><REPONSE observer='Core.BialogDox' ");
			}
		});

test(
		"Authentification",
		function() {
			ObserverStub.ObserverName = "core.auth";

			this.mHttpTransport.XmlReceved = "<?xml version='1.0' encoding='ISO-8859-1'?><REPONSES><REPONSE observer='core.auth' source_extension='CORE' source_action='authentification'><![CDATA[NEEDAUTH]]></REPONSE></REPONSES>";
			ok(!this.mObserverFactory.setAuthentification("abc", "123"), "Bad");
			equal(this.mHttpTransport.getSession(), "", "Session Bad");

			equal(this.mHttpTransport.XmlParam.size(), 3, 'XmlParam size');
			equal(this.mHttpTransport.XmlParam['WebFile'],
					"CORE/authentification", 'WebFile');
			equal(this.mHttpTransport.XmlParam["username"], "abc", "username");
			equal(this.mHttpTransport.XmlParam["password"], "123", "password");

			this.mHttpTransport.XmlReceved = "<?xml version='1.0' encoding='ISO-8859-1'?><REPONSES><REPONSE observer='core.auth' source_extension='CORE' source_action='authentification'><CONNECTION></CONNECTION><PARAM name='ses' type='str'>admin1176588477</PARAM><![CDATA[OK]]></REPONSE></REPONSES>";
			ok(this.mObserverFactory.setAuthentification("admin", "admin"),
					"auth OK");
			equal(this.mHttpTransport.getSession(), "admin1176588477",
					"Session OK");

			equal(this.mHttpTransport.XmlParam.size(), 3, 'XmlParam size');
			equal(this.mHttpTransport.XmlParam['WebFile'],
					"CORE/authentification", 'WebFile');
			equal(this.mHttpTransport.XmlParam["username"], "admin", "username");
			equal(this.mHttpTransport.XmlParam["password"], "admin", "password");
		});
