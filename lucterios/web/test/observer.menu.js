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

test(
		"Menu_Simple",
		function() {
			var xml_receive = "<REPONSE observer='core.menu' source_extension='CORE' source_action='menu'>"
					+ "<TITLE><![CDATA[Menu de l application]]></TITLE>"
					+ "<CONTEXT></CONTEXT>"
					+ "<MENUS>"
					+ "<MENU id='_General' shortcut='' icon='images/general.png' sizeicon='4059' extension='CORE'><![CDATA[_Général]]><HELP><![CDATA[Généralité]]></HELP>"
					+ "	<MENU id='Moncompte' shortcut='shift ctrl alt M' icon='extensions/org_lucterios_contacts/images/fiche.png' sizeicon='2223' extension='org_lucterios_contacts' action='FichePersonnel' modal='1'><![CDATA[Mon compte]]><HELP><![CDATA[Visualiser la fiche de mon compte.]]></HELP></MENU>"
					+ "	<MENU id='Noscoordonnees' shortcut='shift ctrl alt N' icon='extensions/org_lucterios_contacts/images/nousContact.png' sizeicon='5544' extension='org_lucterios_contacts' action='StructureLocal' modal='1'><![CDATA[Nos coordonnées]]><HELP><![CDATA[Fiche complète de notre structure et de ses responsables]]></HELP></MENU>"
					+ "	<MENU id='_MiseajoursetInstallation' shortcut='ctrl alt shift I' icon='extensions/org_lucterios_updates/images/update.png' sizeicon='717' extension='org_lucterios_updates' action='ModulesToUpgrade_APAS_SelectionUpgrade' modal='1'><![CDATA[_Mise à jours et Installation]]><HELP><![CDATA[Téléchargement des dernières mises à jour de votre logiciel.]]></HELP></MENU>"
					+ "	<MENU id='_Motdepasse' shortcut='' icon='images/passwd.png' sizeicon='5026' extension='CORE' action='users_APAS_changerpassword' modal='1'><![CDATA[_Mot de passe]]><HELP><![CDATA[Changement de votre mot de passe.]]></HELP></MENU>"
					+ "</MENU>"
					+ "<MENU id='Ad_ministration' shortcut='' icon='images/admin.png' sizeicon='5104' extension='CORE'><![CDATA[Ad_ministration]]><HELP><![CDATA[Adminitration des configurations et des réglages.]]></HELP>"
					+ "	<MENU id='Configuration_generale' shortcut='' icon='images/config.png' sizeicon='10168' extension='CORE' action='configuration' modal='1'><![CDATA[Configuration _générale]]><HELP><![CDATA[Visualisation et modification des paramètres généraux.]]></HELP></MENU>"
					+ "	<MENU id='Ar_chivage' shortcut='' icon='images/backup.png' sizeicon='4983' extension='CORE'><![CDATA[Ar_chivage]]><HELP><![CDATA[Outils de sauvegarde et de restoration des données.]]></HELP>"
					+ "		<MENU id='_Sauvegarder' shortcut='' icon='images/backup_save.png' sizeicon='5373' extension='CORE' action='selectNewArchive' modal='1'><![CDATA[_Sauvegarder]]><HELP><![CDATA[Sauvegarde manuelle des données du logiciel.]]></HELP></MENU>"
					+ "		<MENU id='_Restauration' shortcut='' icon='images/backup_restor.png' sizeicon='5373' extension='CORE' action='selectRestor' modal='1'><![CDATA[_Restauration]]><HELP><![CDATA[Restauration d'une archive.]]></HELP></MENU>"
					+ "		<MENU id='_Gestiondesarchives' shortcut='' icon='images/backup_tool.png' sizeicon='5451' extension='CORE' action='toolBackup' modal='1'><![CDATA[_Gestion des archives]]><HELP><![CDATA[Importer ou télécharger des archives de sauvegarde]]></HELP></MENU>"
					+ "	</MENU>"
					+ "	<MENU id='_Avance' shortcut='' extension='CORE'><![CDATA[_Avancé]]>"
					+ "		<MENU id='_Parametres' shortcut='' extension='CORE' action='extension_params_APAS_list'><![CDATA[_Paramètres]]></MENU>"
					+ "		<MENU id='Autorisationd`acces_reseau' shortcut='' extension='CORE' action='access_APAS_list'><![CDATA[Autorisation d`accès _réseau]]></MENU>"
					+ "		<MENU id='_Session' shortcut='' extension='CORE' action='sessions_APAS_list'><![CDATA[_Session]]></MENU>"
					+ "	</MENU>" + "</MENU>" + "</MENUS>" + "</REPONSE>";

			var parse = xml_receive.parseXML();
			var obs = new ObserverMenu();
			obs.setSource("CORE", "menu");
			obs.setContent(parse);
			obs.show("");

			var gui = obs.getGUI();
			ok(gui == null, "getGUI");

			var jcnt = $("#menuContainer");

			var lbl = jcnt.find("div:eq(0) > ul:eq(0) > li:eq(0) > a:eq(0)");
			equal(lbl.text(), 'Général', 'tab 1');
			var lbl = jcnt.find("div:eq(0) > ul:eq(0) > li:eq(1) > a:eq(0)");
			equal(lbl.text(), 'Administration', 'tab 2');

			var btn1 = jcnt.find("div:eq(0) > div:eq(0) > button:eq(1)");
			equal(
					btn1.text(),
					'Nos coordonnéesFiche complète de notre structure et de ses responsables',
					'btn 1');

			var btn2 = jcnt.find("div:eq(0) > div:eq(1) > button:eq(3)");
			equal(
					btn2.text(),
					'Gestion des archivesImporter ou télécharger des archives de sauvegarde',
					'btn 2');

			equal(this.mObsFactory.CallList.size(), 0, "Call Nb A");

			btn1.click();
			equal(this.mObsFactory.CallList.size(), 1, "Call Nb B");
			var expected_cmd = "org_lucterios_contacts->StructureLocal()";
			equal(this.mObsFactory.CallList.get(0), expected_cmd, "Call #1");

			btn2.click();
			equal(this.mObsFactory.CallList.size(), 2, "Call Nb C");
			var expected_cmd = "CORE->toolBackup()";
			equal(this.mObsFactory.CallList.get(1), expected_cmd, "Call #2");

			obs.close();
		});

test(
		"Menu_Status",
		function() {
			var xml_receive = "<REPONSE observer='core.menu' source_extension='CORE' source_action='menu'>"
					+ "<TITLE><![CDATA[Menu de l application]]></TITLE>"
					+ "<CONTEXT></CONTEXT>"
					+ "<MENUS>"
					+ "<MENU id='_General' shortcut='' icon='images/general.png' sizeicon='4059' extension='CORE'><![CDATA[_Général]]><HELP><![CDATA[Généralité]]></HELP>"
					+ "	<MENU id='Moncompte' shortcut='shift ctrl alt M' icon='extensions/org_lucterios_contacts/images/fiche.png' sizeicon='2223' extension='org_lucterios_contacts' action='FichePersonnel' modal='1'><![CDATA[Mon compte]]><HELP><![CDATA[Visualiser la fiche de mon compte.]]></HELP></MENU>"
					+ "	<MENU id='Noscoordonnees' shortcut='shift ctrl alt N' icon='extensions/org_lucterios_contacts/images/nousContact.png' sizeicon='5544' extension='org_lucterios_contacts' action='StructureLocal' modal='1'><![CDATA[Nos coordonnées]]><HELP><![CDATA[Fiche complète de notre structure et de ses responsables]]></HELP></MENU>"
					+ "	<MENU id='_MiseajoursetInstallation' shortcut='ctrl alt shift I' icon='extensions/org_lucterios_updates/images/update.png' sizeicon='717' extension='org_lucterios_updates' action='ModulesToUpgrade_APAS_SelectionUpgrade' modal='1'><![CDATA[_Mise à jours et Installation]]><HELP><![CDATA[Téléchargement des dernières mises à jour de votre logiciel.]]></HELP></MENU>"
					+ "	<MENU id='_Motdepasse' shortcut='' icon='images/passwd.png' sizeicon='5026' extension='CORE' action='users_APAS_changerpassword' modal='1'><![CDATA[_Mot de passe]]><HELP><![CDATA[Changement de votre mot de passe.]]></HELP></MENU>"
					+ "</MENU>"
					+ "<MENU id='menu_sup' shortcut=''>"
					+ "	<MENU id='menu_status' shortcut='' icon='images/status.png' sizeicon='5796' extension='CORE' action='status' modal='0'><![CDATA[Résumé]]></MENU>"
					+ "	<MENU id='menu_taches' shortcut='' icon='extensions/org_lucterios_task/images/task.png' sizeicon='3027' extension='org_lucterios_task' action='menuTab' modal='0'><![CDATA[Taches courantes]]></MENU>"
					+ "</MENU>" + "</MENUS>" + "</REPONSE>";

			var parse = xml_receive.parseXML();
			var obs = new ObserverMenu();
			obs.setSource("CORE", "menu");
			obs.setContent(parse);
			obs.show("");

			var gui = obs.getGUI();
			ok(gui == null, "getGUI");

			var jcnt = $("#menuContainer");

			obs.close();
		});
