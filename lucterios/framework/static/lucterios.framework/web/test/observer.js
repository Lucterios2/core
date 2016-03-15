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
			var xml_receive = "<REPONSE observer='core.auth' source_extension='CORE' source_action='authentification'>"
					+ "<CONNECTION>"
					+ "	<TITLE>Lucterios standard</TITLE><SUBTITLE>Application générique de gestion</SUBTITLE>"
					+ "	<VERSION>1.4.2.5</VERSION><SERVERVERSION>1.2.5.606</SERVERVERSION>"
					+ "	<COPYRIGHT>General Public Licence - http://www.lucterios.org</COPYRIGHT>"
					+ "	<LOGONAME>http://demo.lucterios.org/Lucterios/extensions/applis/images/logo.gif</LOGONAME>"
					+ "	<LOGIN>admin</LOGIN><REALNAME>Administrateur</REALNAME>"
					+ "	<SUPPORT_EMAIL><![CDATA[Support Lucterios <support@lucterios.org>]]></SUPPORT_EMAIL><INFO_SERVER><![CDATA[{[italic]}Apache/2.2.14 (Ubuntu){[/italic]}]]></INFO_SERVER>"
					+ "</CONNECTION>"
					+ "<PARAM name='ses' type='str'>admin1315821586</PARAM>"
					+ "<![CDATA[OK]]></REPONSE>";

			var parse = xml_receive.parseXML();
			var obs = new ObserverAuthentification();
			obs.setSource("CORE", "Auth");
			obs.setContent(parse);
			obs.show("Mon titre");

			equal(obs.getGUI(), null, "getGUI");

			var description = Singleton().mDesc;
			equal(description.getTitle(), "Lucterios standard", "Title");
			equal(description.getApplisVersion(), "1.4.2.5", "ApplisVersion");
			equal(description.getServerVersion(), "1.2.5.606", "ServerVersion");
			equal(description.getCopyRigth(),
					"General Public Licence - http://www.lucterios.org",
					"CopyRigth");
			equal(
					description.getLogoIconName(),
					"http://demo.lucterios.org/Lucterios/extensions/applis/images/logo.gif",
					"LogoIconName");
			equal(description.getInfoServer(),
					"{[italic]}Apache/2.2.14 (Ubuntu){[/italic]}", "InfoServer");
			equal(description.getSupportEmail(),
					"Support Lucterios <support@lucterios.org>", "SupportEmail");

			equal(description.getSubTitle(),
					"Application générique de gestion", "SubTitle");
			equal(description.getLogin(), "admin", "Login");
			equal(description.getRealName(), "Administrateur", "RealName");
			equal(Singleton().mRefreshMenu, true, "RefreshMenu");
			equal(obs.getRefreshMenu(), false, "RefreshMenu obs");
			equal(Singleton().Transport().getSession(), 'admin1315821586',
					"session");
		});

test(
		"Authentification 2",
		function() {
			var xml_receive = "<REPONSE observer='core.auth' source_extension='CORE' source_action='authentification'>"
					+ "<![CDATA[BADAUTH]]>" + "</REPONSE>";

			var parse = xml_receive.parseXML();
			var obs = new ObserverAuthentification();
			obs.setSource('CORE', "authentification");
			obs.setContent(parse);
			obs.show("Connexion");

			var gui = obs.getGUI();
			ok(gui != null, "getGUI");
			ok(gui.isExist(), "GUI exist");

			var jcnt = gui.getHtmlDom();

			var lbl = jcnt
					.find("table:eq(0) > tbody > tr:eq(0) > td:eq(0) > label");
			equal(lbl.text(), "Alias ou Mot de passe incorrect!", 'text 1');

			var lbl = jcnt
					.find("table:eq(0) > tbody > tr:eq(1) > td:eq(0) > span");
			equal(lbl.html(), "<b>Alias</b>", 'text 2');

			var lbl = jcnt
					.find("table:eq(0) > tbody > tr:eq(1) > td:eq(1) > input");
			equal(lbl.val(), "", 'alias');
			lbl.val('machin')

			var lbl = jcnt
					.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0) > span");
			equal(lbl.html(), "<b>Mot de passe</b>", 'text 3');

			var lbl = jcnt
					.find("table:eq(0) > tbody > tr:eq(2) > td:eq(1) > input");
			equal(lbl.val(), "", 'MdP');
			lbl.val('coucou')

			var btn1 = jcnt.parent().find(
					"div:eq(2) > div:eq(0) > button:eq(0)");
			equal(btn1.text(), 'Ok', 'btn 1');
			var btn2 = jcnt.parent().find(
					"div:eq(2) > div:eq(0) > button:eq(1)");
			equal(btn2.text(), 'Annuler', 'btn 2');

			equal(this.mObsFactory.CallList.size(), 0, "Call A Nb");

			btn1.click();

			ok(!gui.isExist(), "GUI exist again");
			equal(this.mObsFactory.CallList.size(), 1, "Call B Nb");
			equal(
					this.mObsFactory.CallList.get(0),
					"CORE->authentification(username='machin',password='coucou',)",
					"Call #1");
		});

test(
		"Authentification 3",
		function() {
			var xml_receive = "<REPONSE observer='core.auth' source_extension='CORE' source_action='authentification'>"
					+ "<![CDATA[BADSESS]]>" + "</REPONSE>";

			var parse = xml_receive.parseXML();
			var obs = new ObserverAuthentification();
			obs.setSource('CORE', "authentification");
			obs.setContent(parse);
			obs.show("Connexion");

			var gui = obs.getGUI();
			ok(gui != null, "getGUI");
			ok(gui.isExist(), "GUI exist");

			var jcnt = gui.getHtmlDom();

			var lbl = jcnt
					.find("table:eq(0) > tbody > tr:eq(0) > td:eq(0) > label");
			equal(lbl.text(), "Session expirée !", 'text 1');

			var btn1 = jcnt.parent().find(
					"div:eq(2) > div:eq(0) > button:eq(0)");
			equal(btn1.text(), 'Ok', 'btn 1');
			var btn2 = jcnt.parent().find(
					"div:eq(2) > div:eq(0) > button:eq(1)");
			equal(btn2.text(), 'Annuler', 'btn 2');

			Singleton().mDesc = 0;
			equal(this.mObsFactory.CallList.size(), 0, "Call A Nb");
			equal(this.mCalled, 0, "Called B");

			btn2.click();

			ok(!gui.isExist(), "GUI exist again");
			equal(this.mObsFactory.CallList.size(), 0, "Call B Nb");

			equal(this.mCalled, 1, "Called B");
			equal(Singleton().mDesc, null, 'Desc null');
		});

test(
		"Acknowledge",
		function() {
			var xml_receive = "<REPONSE>"
					+ "<TITLE><![CDATA[Valider]]></TITLE>"
					+ "<CONTEXT><PARAM name='SuperTableTest'><![CDATA[101]]></PARAM></CONTEXT>"
					+ "<ACTION extension='TestValidation' action='SuperTableTest_APAS_Fiche' close='1' modal='1'><![CDATA[editer]]></ACTION>"
					+ "<CLOSE_ACTION><ACTION extension='CORE' action='UNLOCK' close='1' modal='1' unique='1'><![CDATA[unlock]]></ACTION></CLOSE_ACTION>"
					+ "</REPONSE>";

			var parse = xml_receive.parseXML();
			var obs = new ObserverAcknowledge();
			obs.setSource("CORE", "validerAct");
			obs.setContent(parse);
			obs.show("Mon titre");

			ok(obs.getGUI() == null, "getGUI");

			equal(obs.getContext().size(), 1, "Context size");
			equal(obs.getContext().get("SuperTableTest"), "101", "Context 1");

			ok(obs.getRedirectAction() != null, "RedirectAction");
			equal(obs.getRedirectAction().getExtension(), "TestValidation",
					"RedirectAction-Extension");
			equal(obs.getRedirectAction().getAction(),
					"SuperTableTest_APAS_Fiche", "RedirectAction-Action");

			equal(this.mObsFactory.CallList.size(), 2, "Call Nb");
			equal(this.mObsFactory.CallList.get(0),
					"CORE->UNLOCK(SuperTableTest='101',)", "Call #1");
			equal(
					this.mObsFactory.CallList.get(1),
					"TestValidation->SuperTableTest_APAS_Fiche(SuperTableTest='101',)",
					"Call #2");
		});

test(
		"Exception1",
		function() {
			Singleton().mDesc = new ApplicationDescription("aa", "bb", "cc",
					"dd", "ee");
			var xml_receive = "<REPONSE>"
					+ "<TITLE><![CDATA[]]></TITLE>"
					+ "<CONTEXT></CONTEXT>"
					+ "<EXCEPTION>"
					+ "<MESSAGE><![CDATA[Critique]]></MESSAGE>"
					+ "<CODE><![CDATA[1]]></CODE>"
					+ "<MODE><![CDATA[0]]></MODE>"
					+ "<DEBUG_INFO><![CDATA[0|[TestValidation]TableTest::ValiderErreur(act)|57|TableTest::ValiderErreur{[newline]}1|[CORE]BoucleReponse(inc)|81|call_user_func{[newline]}2|[CORE]BoucleReponse(inc)|118|callAction{[newline]}3|[init]|96|BoucleReponse{[newline]}]]></DEBUG_INFO>"
					+ "<TYPE><![CDATA[LucteriosException]]></TYPE>"
					+ "<USER_INFO><![CDATA[]]></USER_INFO>" + "</EXCEPTION>"
					+ "</REPONSE>";

			var parse = xml_receive.parseXML();
			var obs = new ObserverException();
			obs.setSource("CORE", "validerAct");
			obs.setContent(parse);
			obs.show("Mon titre");

			var gui = obs.getGUI();
			ok(gui != null, "getGUI");
			ok(gui.isExist(), "GUI exist");

			var jcnt = gui.getHtmlDom();
			var img = jcnt
					.find("table:eq(0) > tbody > tr:eq(0) > td:eq(0) > img");
			equal(img.attr('src').substr(-9), 'error.png', "image");

			var lbl = jcnt
					.find("table:eq(0) > tbody > tr:eq(0) > td:eq(1) > label");
			equal(lbl.text(), 'Critique', 'text');

			var btn1 = jcnt
					.find("table:eq(0) > tbody > tr:eq(1) > td:eq(0) > input[name='info']");
			equal(btn1.attr('value'), '>>', 'btn 1');
			equal(btn1.attr('type'), 'button', 'btn 1');
			var btn2 = jcnt
					.find("table:eq(0) > tbody > tr:eq(1) > td:eq(0) > input[name='send']");
			equal(btn2.attr('value'), 'Envoyer au support', 'btn 2');
			equal(btn2.attr('type'), 'button', 'btn 2');

			var memo = jcnt
					.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0) > div > div > pre");
			equal(
					memo.text(),
					"[TestValidation]TableTest::ValiderErreur(act)     57   TableTest::ValiderErreur\n"
							+ "[CORE]BoucleReponse(inc)                          81   call_user_func\n"
							+ "[CORE]BoucleReponse(inc)                          118  callAction\n"
							+ "[init]                                            96   BoucleReponse",
					"stack");

			var lbl = jcnt
					.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0) > div > div > label");
			equal(lbl.text(), 'LucteriosException', 'extra');

			equal(this.mObsFactory.CallList.size(), 0, "Call Nb");
			gui.close();
			ok(!gui.isExist(), "GUI remove");
		});

test(
		"Exception2",
		function() {
			var xml_receive = "<REPONSE>"
					+ "<TITLE><![CDATA[]]></TITLE>"
					+ "<CONTEXT></CONTEXT>"
					+ "<EXCEPTION>"
					+ "<MESSAGE><![CDATA[Mineur]]></MESSAGE>"
					+ "<CODE><![CDATA[4]]></CODE>"
					+ "<MODE><![CDATA[0]]></MODE>"
					+ "<DEBUG_INFO><![CDATA[0|[TestValidation]TableTest::ValiderErreur(act)|66|TableTest::ValiderErreur{[newline]}1|[CORE]BoucleReponse(inc)|81|call_user_func{[newline]}2|[CORE]BoucleReponse(inc)|118|callAction{[newline]}3|[init]|96|BoucleReponse{[newline]}]]></DEBUG_INFO>"
					+ "<TYPE><![CDATA[LucteriosException]]></TYPE>"
					+ "<USER_INFO><![CDATA[]]></USER_INFO>" + "</EXCEPTION>"
					+ "</REPONSE>";

			var parse = xml_receive.parseXML();
			var obs = new ObserverException();
			obs.setSource("CORE", "validerAct");
			obs.setContent(parse);
			obs.show("Mon titre");

			var gui = obs.getGUI();
			ok(gui != null, "getGUI");
			ok(gui.isExist(), "GUI exist");

			var jcnt = gui.getHtmlDom();
			var img = jcnt.find("table > tbody > tr:eq(0) > td:eq(0) > img");
			equal(img.attr('src').substr(-8), 'info.png', "image");

			var lbl = jcnt.find("table > tbody > tr:eq(0) > td:eq(1) > label");
			equal(lbl.text(), 'Mineur', 'text');

			var btn1 = jcnt
					.find("table:eq(0) > tbody > tr:eq(1) > td:eq(0) > input");
			equal(btn1.length, 0, 'no btn 1');
			var btn2 = jcnt
					.find("table:eq(0) > tbody > tr:eq(1) > td:eq(1) > input");
			equal(btn2.length, 0, 'no btn 2');

			var memo = jcnt
					.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0) > div > div > pre");
			equal(memo.length, 0, "no stack");

			var lbl = jcnt
					.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0) > div > div > label");
			equal(lbl.length, 0, 'no extra');

			equal(this.mObsFactory.CallList.size(), 0, "Call Nb");
			gui.close();
			ok(!gui.isExist(), "GUI remove");
		});

test(
		"Print",
		function() {
			var xml_receive = "<REPONSE>"
					+ "<TITLE><![CDATA[Imprimer une liste de personneMorale]]></TITLE>"
					+ "<CONTEXT><PARAM name='Filtretype'><![CDATA[2]]></PARAM><PARAM name='PRINT_MODE'><![CDATA[4]]></PARAM></CONTEXT>"
					+ "<PRINT title='Liste des Personnes Morales' type='2' mode='4' withTextExport='1'>"
					+ "<![CDATA[CiJMaXN0ZSBkZXMgUGVyc29ubmVzIE1vcmFsZXMiCgoKIlJhaXNvbiBTb2NpYWxlIjsiQWRyZXNzZSI7IlTpbOlwaG9uZXMiOyJDb3VycmllbCI7CiJMZXMgcCd0aXQgTWlja2V5IjsicGxhY2UgR3JlbmV0dGUgMzgwMDAgR1JFTk9CTEUgRlJBTkNFIjsiMDQuMTIuMzQuNTYuNzggMDYuOTguNzYuNTQuMzIiOyJwZXRpdC5taWNrZXlAZnJlZS5mciI7CiJMZSBnbG9zIG1pbmV0IjsiQ291cnMgQmVyaWF0IDM4MDAwIEdSRU5PQkxFIEZSQU5DRSI7IjA0LjE5LjI4LjM3LjQ2IjsiZ2xvcy5taW5ldEBob3RtYWlsLmZyIjsKImpqaiI7ImpqaiA2NDAwMCBQQVUgRlJBTkNFIjsiIjsibGF1cmVudDM4NjAwQGZyZWUuZnIiOwoKCiIiCgoK]]>"
					+ "</PRINT>" + "</REPONSE>";

			Singleton().mFileManager = this;
			equal(this.mFileContent, null, "Empty file");
			var parse = xml_receive.parseXML();
			var obs = new ObserverPrint();
			obs.setSource("CORE", "validerAct");
			obs.setContent(parse);
			obs.show("Mon titre");

			equal(obs.getContext().size(), 2, "Context size");
			equal(obs.getContext().get("Filtretype"), "2", "Context 1");
			equal(obs.getContext().get("PRINT_MODE"), "4", "Context 2");
			equal(obs.mode, MODE_EXPORT_CSV, 'mode');
			equal(obs.title, 'Liste des Personnes Morales', 'title');

			ok(this.mFileContent != null, "File write");
			var contents = this.mFileContent.split('\n');
			equal(contents.length, 14, "File size");
			equal(contents[1].trim(), "\"Liste des Personnes Morales\"",
					"title");
			equal(
					contents[4].trim(),
					"\"Raison Sociale\";\"Adresse\";\"Téléphones\";\"Courriel\";",
					"header");
			equal(
					contents[6].trim(),
					"\"Le glos minet\";\"Cours Beriat 38000 GRENOBLE FRANCE\";\"04.19.28.37.46\";\"glos.minet@hotmail.fr\";",
					"line #2");
			equal(this.mFileName, 'Liste_des_Personnes_Morales.csv',
					'file name');
			equal(this.mObsFactory.CallList.size(), 0, "Call Nb");
		});

test(
		"Dialog",
		function() {
			var xml_receive = "<REPONSE>"
					+ "<TITLE><![CDATA[Confirmation]]></TITLE>"
					+ "<CONTEXT>"
					+ "<PARAM name='Filtretype'><![CDATA[2]]></PARAM>"
					+ "<PARAM name='ORIGINE'><![CDATA[personneMorale_APAS_Fiche]]></PARAM>"
					+ "<PARAM name='RECORD_ID'><![CDATA[100]]></PARAM>"
					+ "<PARAM name='TABLE_NAME'><![CDATA[org_lucterios_contacts_personneMorale]]></PARAM>"
					+ "<PARAM name='abstractContact'><![CDATA[1196]]></PARAM>"
					+ "<PARAM name='personneMorale'><![CDATA[100]]></PARAM>"
					+ "<PARAM name='CONFIRME'><![CDATA[YES]]></PARAM>"
					+ "</CONTEXT>"
					+ "<TEXT type='2'><![CDATA[Voulez vous supprimer 'jjj'?]]></TEXT>"
					+ "<ACTIONS>"
					+ "<ACTION icon='images/ok.png' sizeicon='1731' extension='org_lucterios_contacts' action='personneAbstraite_APAS_Delete' close='0' modal='1'><![CDATA[Oui]]></ACTION>"
					+ "<ACTION icon='images/cancel.png' sizeicon='1656'><![CDATA[Non]]></ACTION>"
					+ "</ACTIONS>" + "</REPONSE>";

			var parse = xml_receive.parseXML();
			var obs = new ObserverDialogBox();
			obs
					.setSource("org_lucterios_contacts",
							"personneMorale_APAS_Fiche");
			obs.setContent(parse);
			obs.show("Confirmation");

			var gui = obs.getGUI();
			ok(gui != null, "getGUI");
			ok(gui.isExist(), "GUI exist");

			var jcnt = gui.getHtmlDom();
			var img = jcnt
					.find("table:eq(0) > tbody > tr:eq(0) > td:eq(0) > img");
			equal(img.attr('src').substr(-11), 'confirm.png', "image");

			var lbl = jcnt
					.find("table:eq(0) > tbody > tr:eq(0) > td:eq(1) > label");
			equal(lbl.text(), "Voulez vous supprimer 'jjj'?", 'text');

			var btn1 = jcnt.parent().find(
					"div:eq(2) > div:eq(0) > button:eq(0)");
			equal(btn1.text(), 'Oui', 'btn 1');
			var btn2 = jcnt.parent().find(
					"div:eq(2) > div:eq(0) > button:eq(1)");
			equal(btn2.text(), 'Non', 'btn 2');

			equal(obs.getContext().size(), 7, "Context size");
			equal(obs.getContext().get("personneMorale"), "100", "Context 1");
			equal(obs.getContext().get("CONFIRME"), "YES", "Context 2");

			equal(this.mObsFactory.CallList.size(), 0, "Call A Nb");

			btn1.click();

			ok(gui.isExist(), "GUI exist again");
			equal(this.mObsFactory.CallList.size(), 2, "Call B Nb");
			equal(
					this.mObsFactory.CallList.get(0),
					"org_lucterios_contacts->personneAbstraite_APAS_Delete(Filtretype='2',ORIGINE='personneMorale_APAS_Fiche',RECORD_ID='100',TABLE_NAME='org_lucterios_contacts_personneMorale',abstractContact='1196',personneMorale='100',CONFIRME='YES',)",
					"Call #1");
			equal(
					this.mObsFactory.CallList.get(1),
					"org_lucterios_contacts->personneMorale_APAS_Fiche(Filtretype='2',ORIGINE='personneMorale_APAS_Fiche',RECORD_ID='100',TABLE_NAME='org_lucterios_contacts_personneMorale',abstractContact='1196',personneMorale='100',CONFIRME='YES',)",
					"Call #2");

			btn2.click();
			ok(!gui.isExist(), "GUI close");
			equal(this.mObsFactory.CallList.size(), 2, "Call C Nb :"
					+ this.mObsFactory.CallList.toString());
		});
