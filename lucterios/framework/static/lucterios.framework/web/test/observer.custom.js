var ObserverAcknowledgeNoParent = ObserverAcknowledge.extend({
	setParent : function(aParent) {
		this.mParent = null;
	},
});

module('ObserverCustom', {
	mFileContent : null,
	mCalled : 0,

	setup : function() {
		this.mObsFactory = new ObserverFactoryMock();

		Singleton().setHttpTransportClass(HttpTransportStub);
		Singleton().setFactory(this.mObsFactory);
		Singleton().setActionClass(ActionImpl);
		Singleton().Transport().setSession("abc123");
		Singleton().mSelectLang = 'fr';

		ObserverFactoryMock.NewObserver = new ObserverAcknowledgeNoParent();
		ObserverAuthentification.connectSetValue = this.setValue;
	},
	teardown : function() {
		ObserverAuthentification.connectSetValue = null;
		SingletonClose();
	},

	saveBlob : function(aBlob, aFileName) {
		this.mFileContent = aBlob;
		this.mFileName = aFileName;
	},
});

test(
		"Custom_Simple",
		function() {
			var xml_receive = "<REPONSE>"
					+ "<TITLE><![CDATA[Résumé]]></TITLE>"
					+ "<CONTEXT></CONTEXT>"
					+ "<COMPONENTS>"
					+ "<LABELFORM name='documenttitle' description=''  tab='0' x='0' y='70' colspan='4' rowspan='1'><![CDATA[{[center]}{[bold]}{[underline]}Gestion documentaire{[/underline]}{[/bold]}{[/center]}]]></LABELFORM>"
					+ "<LABELFORM name='lbl_nbdocument' description=''  tab='0' x='0' y='71' colspan='4' rowspan='1'><![CDATA[{[center]}13 fichiers actuellement disponibles{[/center]}]]></LABELFORM>"
					+ "<LABELFORM name='lbl_remainingsize' description=''  tab='0' x='0' y='72' colspan='4' rowspan='1'><![CDATA[{[center]}{[italic]}Taille de stockage: restant 30.03 Mo. sur 1 Go.{[/italic]}{[/center]}]]></LABELFORM>"
					+ "<LABELFORM name='documentend' description=''  tab='0' x='0' y='73' colspan='4' rowspan='1'><![CDATA[{[center]}{[hr/]}{[/center]}]]></LABELFORM>"
					+ "<LABELFORM name='updatestitle' description=''  tab='0' x='0' y='100' colspan='4' rowspan='1'><![CDATA[{[center]}{[bold]}{[underline]}Mises à jour{[/underline]}{[/bold]}{[/center]}]]></LABELFORM>"
					+ "<LABELFORM name='updatelbl' description=''  tab='0' x='0' y='101' colspan='4' rowspan='1'><![CDATA[{[center]}Votre logiciel est à jour.{[/center]}]]></LABELFORM>"
					+ "<LABELFORM name='updatesend' description=''  tab='0' x='0' y='103' colspan='4' rowspan='1'><![CDATA[{[center]}{[hr/]}{[/center]}]]></LABELFORM>"
					+ "</COMPONENTS>" + "</REPONSE>";

			var parse = xml_receive.parseXML();
			var obs = new ObserverCustom();
			obs.setSource("CORE", "status");
			obs.setContent(parse);
			obs.show("Résumé", FORM_MODAL);

			var gui = obs.getGUI();
			ok(gui != null, "getGUI");
			ok(gui.isExist(), "GUI exist");
			var jcnt = gui.getHtmlDom();

			var lbl = jcnt
					.find("table:eq(0) > tbody > tr:eq(0) > td:eq(0) > span");
			equal(lbl.html(),
					"<center><b><u>Gestion documentaire</u></b></center>",
					"text 1");

			var lbl = jcnt
					.find("table:eq(0) > tbody > tr:eq(1) > td:eq(0) > span");
			equal(lbl.html(),
					"<center>13 fichiers actuellement disponibles</center>",
					"text 2");

			var lbl = jcnt
					.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0) > span");
			equal(
					lbl.html(),
					"<center><i>Taille de stockage: restant 30.03 Mo. sur 1 Go.</i></center>",
					"text 3");

			var lbl = jcnt
					.find("table:eq(0) > tbody > tr:eq(3) > td:eq(0) > span");
			equal(lbl.html(), "<center><hr></center>", "text 4");

			var lbl = jcnt
					.find("table:eq(0) > tbody > tr:eq(4) > td:eq(0) > span");
			equal(lbl.html(), "<center><b><u>Mises à jour</u></b></center>",
					"text 5");

			var lbl = jcnt
					.find("table:eq(0) > tbody > tr:eq(5) > td:eq(0) > span");
			equal(lbl.html(), "<center>Votre logiciel est à jour.</center>",
					"text 6");

			var lbl = jcnt
					.find("table:eq(0) > tbody > tr:eq(6) > td:eq(0) > span");
			equal(lbl.html(), "<center><hr></center>", "text 7");
			equal(this.mObsFactory.CallList.size(), 0, "Call Nb");

			var btn1 = jcnt.parent().find(
					"div:eq(2) > div:eq(0) > button:eq(0)");
			equal(btn1.text(), 'Fermer', 'btn 1');
			var btn2 = jcnt.parent().find(
					"div:eq(2) > div:eq(0) > button:eq(1)");
			equal(btn2.text(), '', 'btn 2');

			obs.close();
			ok(!gui.isExist(), "GUI exist");
			equal(this.mObsFactory.CallList.size(), 0, "Call Nb");
		});

test(
		"Custom_EditMemo",
		function() {
			var xml_receive = "<REPONSE observer='core.custom' source_extension='org_lucterios_contacts' source_action='personneMorale_APAS_AddModify'>"
					+ "<TITLE><![CDATA[Modifier une personne morale]]></TITLE>"
					+ "<CONTEXT><PARAM name='personneMorale'><![CDATA[1]]></PARAM><PARAM name='ORIGINE'><![CDATA[personneMorale_APAS_AddModify]]></PARAM><PARAM name='TABLE_NAME'><![CDATA[org_lucterios_contacts_personneMorale]]></PARAM><PARAM name='RECORD_ID'><![CDATA[1]]></PARAM></CONTEXT>"
					+ "<COMPONENTS>"
					+ "	<IMAGE name='img' description=''  tab='0' x='0' y='0' colspan='1' rowspan='3' size='8310' height='64' width='64' ><TYPE><![CDATA[]]></TYPE><![CDATA[extensions/org_lucterios_contacts/images/contactMoral.png]]></IMAGE>"
					+ "	<LABELFORM name='labelraisonSociale' description=''  tab='0' x='1' y='0' colspan='1' rowspan='1'><![CDATA[{[bold]}Raison Sociale{[/bold]}]]></LABELFORM>"
					+ "	<EDIT name='raisonSociale' description='Raison+Sociale'  tab='0' x='2' y='0' colspan='1' rowspan='1' VMin='20' HMin='150'><![CDATA[Association Multi-sport de démonstration]]><ACTIONS></ACTIONS></EDIT>"
					+ "	<LABELFORM name='labeladresse' description=''  tab='0' x='1' y='1' colspan='1' rowspan='1'><![CDATA[{[bold]}Adresse{[/bold]}]]></LABELFORM>"
					+ "	<MEMO name='adresse' description='Adresse'  tab='0' x='2' y='1' colspan='3' rowspan='1' VMin='50' HMin='200' needed='1' FirstLine='-1'><![CDATA[place central]]><ACTIONS></ACTIONS></MEMO>"
					+ "	<LABELFORM name='labelcodePostal' description=''  tab='0' x='1' y='2' colspan='1' rowspan='1'><![CDATA[{[bold]}Code Postal{[/bold]}]]></LABELFORM>"
					+ "	<EDIT name='codePostal' description='Code+Postal'  tab='0' x='2' y='2' colspan='1' rowspan='1' VMin='20' HMin='150' needed='1'><![CDATA[99000]]><ACTIONS><ACTION extension='org_lucterios_contacts' action='personneMorale_APAS_AddModify' close='0' modal='2' unique='1'><![CDATA[Modifier]]></ACTION></ACTIONS></EDIT>"
					+ "	<LABELFORM name='lblville' description=''  tab='0' x='3' y='2' colspan='1' rowspan='1'><![CDATA[{[bold]}Ville{[/bold]}]]></LABELFORM>"
					+ "	<EDIT name='ville' description=''  tab='0' x='4' y='2' colspan='1' rowspan='1' VMin='20' HMin='150'><![CDATA[TRIFOUILLY]]><ACTIONS></ACTIONS></EDIT>"
					+ "	<LABELFORM name='labelpays' description=''  tab='0' x='1' y='3' colspan='1' rowspan='1'><![CDATA[{[bold]}Pays{[/bold]}]]></LABELFORM>"
					+ "	<EDIT name='pays' description='Pays'  tab='0' x='2' y='3' colspan='1' rowspan='1' VMin='20' HMin='150'><![CDATA[]]><ACTIONS></ACTIONS></EDIT>"
					+ "	<LABELFORM name='labelfixe' description=''  tab='0' x='1' y='4' colspan='1' rowspan='1'><![CDATA[{[bold]}Tel. Fixe{[/bold]}]]></LABELFORM>"
					+ "	<EDIT name='fixe' description='Tel.+Fixe'  tab='0' x='2' y='4' colspan='1' rowspan='1' VMin='20' HMin='150'><![CDATA[0987654321]]><ACTIONS></ACTIONS></EDIT>"
					+ "	<LABELFORM name='labelportable' description=''  tab='0' x='3' y='4' colspan='1' rowspan='1'><![CDATA[{[bold]}Tel. Portable{[/bold]}]]></LABELFORM>"
					+ "	<EDIT name='portable' description='Tel.+Portable'  tab='0' x='4' y='4' colspan='1' rowspan='1' VMin='20' HMin='150'><![CDATA[]]><ACTIONS></ACTIONS></EDIT>"
					+ "	<LABELFORM name='labelfax' description=''  tab='0' x='1' y='5' colspan='1' rowspan='1'><![CDATA[{[bold]}Fax{[/bold]}]]></LABELFORM>"
					+ "	<EDIT name='fax' description='Fax'  tab='0' x='2' y='5' colspan='1' rowspan='1' VMin='20' HMin='150'><![CDATA[]]><ACTIONS></ACTIONS></EDIT>"
					+ "	<LABELFORM name='labelmail' description=''  tab='0' x='1' y='6' colspan='1' rowspan='1'><![CDATA[{[bold]}Courriel{[/bold]}]]></LABELFORM>"
					+ "	<EDIT name='mail' description='Courriel'  tab='0' x='2' y='6' colspan='3' rowspan='1'><![CDATA[info@sd-libre.fr]]><ACTIONS></ACTIONS></EDIT>"
					+ "	<LABELFORM name='labelsiren' description=''  tab='0' x='1' y='31' colspan='1' rowspan='1'><![CDATA[{[bold]}Informations légales{[/bold]}]]></LABELFORM>"
					+ "	<MEMO name='siren' description='Informations+l%E9gales'  tab='0' x='2' y='31' colspan='3' rowspan='1' VMin='50' HMin='200' FirstLine='-1'><![CDATA[]]><ACTIONS></ACTIONS></MEMO>"
					+ "	<LABELFORM name='labelcommentaire' description=''  tab='0' x='1' y='50' colspan='1' rowspan='1'><![CDATA[{[bold]}Commentaire{[/bold]}]]></LABELFORM>"
					+ "	<MEMO name='commentaire' description='Commentaire'  tab='0' x='2' y='50' colspan='3' rowspan='1' VMin='50' HMin='200' FirstLine='-1'><![CDATA[]]><ACTIONS></ACTIONS></MEMO>"
					+ "	<LABEL name='labelnewpass' description=''  tab='0' x='1' y='60' colspan='1' rowspan='1'><![CDATA[{[bold]}Mot de passe{[/bold]}]]></LABEL>"
					+ "	<PASSWD name='newpass' description=''  tab='0' x='2' y='60' colspan='1' rowspan='1'><![CDATA[]]><ACTIONS></ACTIONS></PASSWD>"
					+ "</COMPONENTS>"
					+ "<ACTIONS>"
					+ "	<ACTION icon='images/ok.png' sizeicon='1731' extension='org_lucterios_contacts' action='personneMorale_APAS_AddModifyAct' close='1' modal='1'><![CDATA[_Ok]]></ACTION>"
					+ "	<ACTION icon='images/cancel.png' sizeicon='1656'><![CDATA[_Annuler]]></ACTION>"
					+ "</ACTIONS>"
					+ "<CLOSE_ACTION><ACTION extension='CORE' action='UNLOCK' close='1' modal='1' unique='1'><![CDATA[unlock]]></ACTION></CLOSE_ACTION></REPONSE>";

			var parse = xml_receive.parseXML();
			var obs = new ObserverCustom();
			obs.setSource("CORE", "status");
			obs.setContent(parse);
			obs.show("Nos coordonnées", FORM_MODAL);

			var gui = obs.getGUI();
			ok(gui != null, "getGUI");
			ok(gui.isExist(), "GUI exist");
			var jcnt = gui.getHtmlDom();

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(0) > td:eq(0) > img");
			equal(
					comp.attr("src").substr(0, 67),
					"STUB/extensions/org_lucterios_contacts/images/contactMoral.png?val=",
					"comp 1");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(0) > td:eq(1) > span");
			equal(comp.html(), "<b>Raison Sociale</b>", "comp 2");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(0) > td:eq(2) > input");
			equal(comp.val(), "Association Multi-sport de démonstration",
					"comp 3");
			comp.focus();
			comp.val("AAA");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(1) > td:eq(0) > span");
			equal(comp.html(), "<b>Adresse</b>", "comp 4");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(1) > td:eq(1) > textarea");
			equal(comp.text(), "place central", "comp 5");
			comp.focus();
			comp.text("BBB\nCCC");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0) > span");
			equal(comp.html(), "<b>Code Postal</b>", "comp 6");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(2) > td:eq(1) > input");
			equal(comp.val(), "99000", "comp 7");
			comp.focus();
			comp.val("123456");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(2) > td:eq(2) > span");
			equal(comp.html(), "<b>Ville</b>", "comp 8");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(2) > td:eq(3) > input");
			equal(comp.val(), "TRIFOUILLY", "comp 9");
			comp.focus();
			comp.val("DDDD");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(3) > td:eq(1) > span");
			equal(comp.html(), "<b>Pays</b>", "comp 10");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(3) > td:eq(2) > input");
			equal(comp.val(), "", "comp 11");
			comp.focus();
			comp.val("EEEE");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(4) > td:eq(1) > span");
			equal(comp.html(), "<b>Tel. Fixe</b>", "comp 12");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(4) > td:eq(2) > input");
			equal(comp.val(), "0987654321", "comp 13");
			comp.focus();
			comp.val("FFFFF");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(4) > td:eq(3) > span");
			equal(comp.html(), "<b>Tel. Portable</b>", "comp 14");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(4) > td:eq(4) > input");
			equal(comp.val(), "", "comp 15");
			comp.focus();
			comp.val("GGGGG");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(5) > td:eq(1) > span");
			equal(comp.html(), "<b>Fax</b>", "comp 16");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(5) > td:eq(2) > input");
			equal(comp.val(), "", "comp 17");
			comp.focus();
			comp.val("HHHHH");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(6) > td:eq(1) > span");
			equal(comp.html(), "<b>Courriel</b>", "comp 18");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(6) > td:eq(2) > input");
			equal(comp.val(), "info@sd-libre.fr", "comp 19");
			comp.focus();
			comp.val("IIIII");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(7) > td:eq(1) > span");
			equal(comp.html(), "<b>Informations légales</b>", "comp 20");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(7) > td:eq(2) > textarea");
			equal(comp.text(), "", "comp 21");
			comp.focus();
			comp.text("JJ\nKKKK");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(8) > td:eq(1) > span");
			equal(comp.html(), "<b>Commentaire</b>", "comp 22");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(8) > td:eq(2) > textarea");
			equal(comp.text(), "", "comp 23");
			comp.focus();
			comp.text("LL\nMMMM\nNN");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(9) > td:eq(1) > span");
			equal(comp.html(), "<b>Mot de passe</b>", "comp 24");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(9) > td:eq(2) > input");
			equal(comp.val(), "", "comp 25");
			comp.focus();
			comp.val("abc123");

			var btn1 = jcnt.parent().find(
					"div:eq(2) > div:eq(0) > button:eq(0)");
			equal(btn1.text(), 'Ok', 'btn 1');
			var btn2 = jcnt.parent().find(
					"div:eq(2) > div:eq(0) > button:eq(1)");
			equal(btn2.text(), 'Annuler', 'btn 2');

			this.mObsFactory.init();

			equal(this.mObsFactory.CallList.size(), 0, "Call A null :"
					+ this.mObsFactory.CallList.toString());

			btn1.click();

			ok(!gui.isExist(), "GUI exist");
			equal(this.mObsFactory.CallList.size(), 2, "Call B Nb :"
					+ this.mObsFactory.CallList.toString());
			var expected_cmd = "CORE->UNLOCK(";
			expected_cmd += "personneMorale='1',ORIGINE='personneMorale_APAS_AddModify',TABLE_NAME='org_lucterios_contacts_personneMorale',RECORD_ID='1',";
			expected_cmd += ")";
			equal(this.mObsFactory.CallList.get(0), expected_cmd, "Call #1");
			var expected_cmd = "org_lucterios_contacts->personneMorale_APAS_AddModifyAct(";
			expected_cmd += "personneMorale='1',ORIGINE='personneMorale_APAS_AddModify',TABLE_NAME='org_lucterios_contacts_personneMorale',RECORD_ID='1',";
			expected_cmd += "raisonSociale='AAA',adresse='BBB{[newline]}CCC',codePostal='123456',ville='DDDD',pays='EEEE',";
					expected_cmd += "fixe='FFFFF',portable='GGGGG',fax='HHHHH',mail='IIIII',siren='JJ{[newline]}KKKK',commentaire='LL{[newline]}MMMM{[newline]}NN',newpass='abc123',",
					expected_cmd += ")";
			equal(this.mObsFactory.CallList.get(1), expected_cmd, "Call #2");
		});

asyncTest(
		"Custom_Upload",
		function() {
			var xml_receive = "<REPONSE observer='core.custom' source_extension='org_lucterios_contacts' source_action='personneMorale_APAS_AddModify'>"
					+ "<TITLE><![CDATA[Modifier une personne morale]]></TITLE>"
					+ "<CONTEXT><PARAM name='personneMorale'><![CDATA[1]]></PARAM></CONTEXT>"
					+ "<COMPONENTS>"
					+ "	<LABELFORM name='Lbl_uploadlogo' description=''  tab='0' x='1' y='51' colspan='1' rowspan='1'><![CDATA[{[bold]}Image{[/bold]}]]></LABELFORM>"
					+ "	<UPLOAD name='uploadlogo' description=''  tab='0' x='2' y='51' colspan='3' rowspan='1' maxsize='1048576'><![CDATA[]]><FILTER><![CDATA[.jpg]]></FILTER></UPLOAD>"
					+ "	<LABELFORM name='Lbl_warning' description=''  tab='0' x='1' y='52' colspan='4' rowspan='1'><![CDATA[{[center]}{[italic]}{[font size='-2']}Importer de préférence une image JPEG de 100x100 pts.{[/font]}{[/italic]}{[/center]}]]></LABELFORM>"
					+ "	<LABELFORM name='lblmail' description=''  tab='0' x='1' y='60' colspan='1' rowspan='1'><![CDATA[{[bold]}Courriel{[/bold]}]]></LABELFORM>"
					+ "	<LINK name='mail' description=''  tab='0' x='2' y='60' colspan='3' rowspan='1'><![CDATA[nous écrire]]><LINK><![CDATA[mailto:info@sd-libre.fr]]></LINK></LINK>"
					+ "	<DOWNLOAD name='down' description=''  tab='0' x='1' y='70' colspan='4' rowspan='1' Compress='0' HttpFile='1' maxsize='1048576'><![CDATA[FileName.txt]]>"
					+ "		<FILENAME><![CDATA[usr/TestValidation/FileName.txt]]></FILENAME>"
					+ "		<ACTIONS>"
					+ "			<ACTION icon='images/edit.png' sizeicon='787' extension='TestValidation' action='LoadFile' close='0' modal='1'><![CDATA[Load]]></ACTION>"
					+ "		</ACTIONS>"
					+ "	</DOWNLOAD>"
					+ "</COMPONENTS>"
					+ "<ACTIONS>"
					+ "	<ACTION icon='images/ok.png' sizeicon='1731' extension='org_lucterios_contacts' action='personneMorale_APAS_AddModifyAct' close='1' modal='1'><![CDATA[_Ok]]></ACTION>"
					+ "	<ACTION icon='images/cancel.png' sizeicon='1656'><![CDATA[_Annuler]]></ACTION>"
					+ "</ACTIONS>" + "</REPONSE>";

			var content_file = 'This file is part of Diacamma, a software developped by "Le Sanglier du Libre" (http://www.sd-libre.fr)\n'
					+ 'Thanks to have payed a retribution for using this module.\n'
					+ '\n'
					+ 'Diacamma is free software; you can redistribute it and/or modify\n'
					+ 'it under the terms of the GNU General Public License as published by\n'
					+ 'the Free Software Foundation; either version 2 of the License, or\n'
					+ '(at your option) any later version.\n'
					+ '\n'
					+ 'Diacamma is distributed in the hope that it will be useful,\n'
					+ 'but WITHOUT ANY WARRANTY; without even the implied warranty of\n'
					+ 'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n'
					+ 'GNU General Public License for more details.\n'
					+ '\n'
					+ 'You should have received a copy of the GNU General Public License\n'
					+ 'along with Lucterios; if not, write to the Free Software\n'
					+ 'Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA';

			Singleton().Transport().XmlReceved = content_file;
			Singleton().mFileManager.saveBlob = $.proxy(this.saveBlob, this);
			equal(this.mFileContent, null, "Empty file");

			var parse = xml_receive.parseXML();
			var obs = new ObserverCustom();
			obs.setSource("org_lucterios_contacts",
					"personneMorale_APAS_AddModify");
			obs.setContent(parse);
			obs.show("Nos coordonnées", FORM_MODAL);

			obs.mCompList.get('uploadlogo').getValue = function() {
				if (typeof (Blob) === typeof (Function)) {
					var blob_content = new Blob([ content_file ], {
						type : "text/plain;charset=UTF-8"
					});
					return blob_content;
				} else {
					var builder = new WebKitBlobBuilder();
					builder.append(content_file);
					return blob = builder.getBlob();
				}
			};

			var gui = obs.getGUI();
			ok(gui != null, "getGUI");
			ok(gui.isExist(), "GUI exist");
			var jcnt = gui.getHtmlDom();

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(0) > td:eq(1) > span");
			equal(comp.html(), "<b>Image</b>", "comp 1");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(0) > td:eq(2) > input");
			equal(comp.attr("accept"), ".jpg", "comp 2");
			comp.change();

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(1) > td:eq(1) > span");
			equal(
					comp.html(),
					'<center><i><font size="-2">Importer de préférence une image JPEG de 100x100 pts.</font></i></center>',
					"comp 3");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(2) > td:eq(1) > span");
			equal(comp.html(), '<b>Courriel</b>', "comp 4");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(2) > td:eq(2) > a");
			equal(comp.html(), 'nous écrire', "comp 4");
			equal(comp.attr('href'), 'mailto:info@sd-libre.fr', "comp 4+");

			var comp_lbl = jcnt
					.find("table:eq(0) > tbody > tr:eq(3) > td:eq(1) > label");
			equal(comp_lbl.html(), 'FileName.txt', "comp filename");
			var comp_download = jcnt
					.find("table:eq(0) > tbody > tr:eq(3) > td:eq(1) > button");
			equal(comp_download.text(), 'Enregistrer sous...', "comp download");

			var btn1 = jcnt.parent().find(
					"div:eq(2) > div:eq(0) > button:eq(0)");
			equal(btn1.text(), 'Ok', 'btn 1');
			var btn2 = jcnt.parent().find(
					"div:eq(2) > div:eq(0) > button:eq(1)");
			equal(btn2.text(), 'Annuler', 'btn 2');

			equal(this.mObsFactory.CallList.size(), 0, "Call A Nb :"
					+ this.mObsFactory.CallList.toString());

			comp_download.click();
			equal(this.mFileName, "FileName.txt");
			ok(this.mFileContent != null, "File write");
			equal(this.mFileContent.size, content_file.length);
			equal(Singleton().Transport().XmlParam['URL'],
					'usr/TestValidation/FileName.txt');

			var content_base64 = btoa(content_file);
			var current_factory = this.mObsFactory;
			setTimeout(
					function() {
						start();

						btn1.click();
						ok(!gui.isExist(), "GUI exist");
						equal(current_factory.CallList.size(), 1, "Call B Nb :"
								+ current_factory.CallList.toString());
						var expected_cmd = "org_lucterios_contacts->personneMorale_APAS_AddModifyAct(";
						expected_cmd += "personneMorale='1',uploadlogo='undefined;"
								+ content_base64 + "',"
						expected_cmd += ")";
						equal(current_factory.CallList.get(0), expected_cmd,
								"Call #1");
					}, 600);
		});

test(
		"Custom_advance",
		function() {
			var xml_receive = "<REPONSE observer='core.custom' source_extension='org_lucterios_task' source_action='Tasks_APAS_AddModify'>"
					+ "<TITLE><![CDATA[Ajouter une tâche]]></TITLE>"
					+ "<CONTEXT><PARAM name='isTerminate'><![CDATA[n]]></PARAM><PARAM name='task'><![CDATA[1]]></PARAM></CONTEXT>"
					+ "<COMPONENTS>	<IMAGE name='img' description=''  tab='0' x='0' y='0' colspan='1' rowspan='9' size='3027' height='64' width='64' ><TYPE><![CDATA[]]></TYPE><![CDATA[extensions/org_lucterios_task/images/task.png]]></IMAGE>"
					+ "	<LABELFORM name='labelbegin' description=''  tab='0' x='1' y='2' colspan='1' rowspan='1'><![CDATA[{[bold]}Début{[/bold]}]]></LABELFORM>"
					+ "	<DATE name='begin' description='D%E9but'  tab='0' x='2' y='2' colspan='2' rowspan='1' needed='1'><![CDATA[2012-08-15]]><ACTIONS></ACTIONS></DATE>"
					+ "	<LABELFORM name='labelowner' description=''  tab='0' x='4' y='2' colspan='1' rowspan='1'><![CDATA[{[bold]}Responsable{[/bold]}]]></LABELFORM>"
					+ "	<SELECT name='owner' description=''  tab='0' x='5' y='2' colspan='2' rowspan='1' VMin='20' HMin='200'>143"
					+ "		<CASE id='0'><![CDATA[]]></CASE>"
					+ "		<CASE id='120'><![CDATA[Simon JOLU]]></CASE>"
					+ "		<CASE id='143'><![CDATA[Camille DATAFUFA]]></CASE>"
					+ "		<ACTIONS></ACTIONS>"
					+ "		<JavaScript><![CDATA[%0Avar+owner%3Dcurrent.getValue%28%29%3B%0Aif+%28owner%21%3D143%29+%7B%0A%09parent.get%28%27type%27%29.setEnabled%28false%29%3B%0A%09parent.get%28%27type%27%29.setValue%28%27%3CCHECK%3En%3C%2FCHECK%3E%27%29%3B%0A%7D%0Aelse+%7B%0A%09parent.get%28%27type%27%29.setEnabled%28true%29%3B%0A%7D%0A]]></JavaScript>"
					+ "	</SELECT>"
					+ "	<BUTTON name='NewOwer' description=''  tab='0' x='7' y='2' colspan='1' rowspan='2' isMini='1' clickname='BTN' clickvalue='123'><ACTIONS><ACTION extension='org_lucterios_task' action='Tasks_APAS_SelectResp' close='0' modal='1'><![CDATA[+]]></ACTION></ACTIONS></BUTTON>"
					+ "	<LABELFORM name='labelend' description=''  tab='0' x='1' y='3' colspan='1' rowspan='1'><![CDATA[{[bold]}Fin{[/bold]}]]></LABELFORM>"
					+ "	<TIME name='end' description='Fin'  tab='0' x='2' y='3' colspan='2' rowspan='1' needed='1'><![CDATA[11:30]]><ACTIONS></ACTIONS></TIME>"
					+ "	<LABELFORM name='labeltype' description=''  tab='0' x='4' y='3' colspan='1' rowspan='1'><![CDATA[{[bold]}Privé{[/bold]}]]></LABELFORM>"
					+ "	<CHECK name='type' description='Priv%E9'  tab='0' x='5' y='3' colspan='1' rowspan='1' needed='1'><![CDATA[1]]><ACTIONS></ACTIONS></CHECK>"
					+ "	<LABELFORM name='labelcouleur' description=''  tab='0' x='1' y='4' colspan='1' rowspan='1'><![CDATA[{[bold]}Code couleur{[/bold]}]]></LABELFORM>"
					+ "	<SELECT name='couleur' description='Code+couleur'  tab='0' x='2' y='4' colspan='2' rowspan='1' needed='1'>3"
					+ "		<CASE id='0'><![CDATA[Noir]]></CASE>"
					+ "		<CASE id='1'><![CDATA[Bleu]]></CASE>"
					+ "		<CASE id='2'><![CDATA[Rouge]]></CASE>"
					+ "		<CASE id='3'><![CDATA[Vert]]></CASE>"
					+ "		<CASE id='4'><![CDATA[Jaune]]></CASE>"
					+ "		<CASE id='5'><![CDATA[Violet]]></CASE>"
					+ "		<CASE id='6'><![CDATA[Orange]]></CASE>"
					+ "	</SELECT>"
					+ "	<LABELFORM name='labelrappel' description=''  tab='0' x='4' y='4' colspan='1' rowspan='1'><![CDATA[{[bold]}Rappel (Nb de jours){[/bold]}]]></LABELFORM>"
					+ "	<FLOAT name='rappel' description='Rappel+%28Nb+de+jours%29'  tab='0' x='5' y='4' colspan='2' rowspan='1' needed='1' min='0' max='30' prec='0'><![CDATA[5]]><ACTIONS></ACTIONS></FLOAT>"
					+ "   <LABELFORM name='labelrdv' description=''  tab='0' x='1' y='5' colspan='1' rowspan='1'><![CDATA[{[bold]}Date Heure RDV{[/bold]}]]></LABELFORM>"
					+ "   <DATETIME name='rdv' description=''  tab='0' x='2' y='5' colspan='2' rowspan='1'><![CDATA[2008-07-12 23:47:31]]><ACTIONS></ACTIONS></DATETIME>"
					+ "	<LABELFORM name='labellist' description=''  tab='0' x='4' y='5' colspan='1' rowspan='1'><![CDATA[{[bold]}Listing{[/bold]}]]></LABELFORM>"
					+ "	<CHECKLIST name='list' description=''  tab='0' x='5' y='5' colspan='2' rowspan='1' simple='0'>"
					+ "		<CASE id='1' checked='1'><![CDATA[abc]]></CASE>"
					+ "		<CASE id='2' checked='1'><![CDATA[def]]></CASE>"
					+ "		<CASE id='3' checked='0'><![CDATA[ghij]]></CASE>"
					+ "		<CASE id='4' checked='0'><![CDATA[klmn]]></CASE>"
					+ "	</CHECKLIST>"
					+ "</COMPONENTS>"
					+ "<ACTIONS>"
					+ "	<ACTION icon='images/ok.png' sizeicon='1731' extension='org_lucterios_task' action='Tasks_APAS_AddModifyAct' close='1' modal='1'><![CDATA[_Ok]]></ACTION>"
					+ "	<ACTION icon='images/cancel.png' sizeicon='1656'><![CDATA[_Annuler]]></ACTION>"
					+ "</ACTIONS>" + "</REPONSE>";

			var parse = xml_receive.parseXML();
			var obs = new ObserverCustom();
			obs.setSource("org_lucterios_task", "Tasks_APAS_AddModify");
			obs.setContent(parse);
			obs.show("Modifier", FORM_MODAL);

			var gui = obs.getGUI();
			ok(gui != null, "getGUI");
			ok(gui.isExist(), "GUI exist");
			var jcnt = gui.getHtmlDom();

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(0) > td:eq(0) > img");
			equal(
					comp.attr("src").substr(0, 55),
					"STUB/extensions/org_lucterios_task/images/task.png?val=",
					"comp img");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0) > span");
			equal(comp.html(), "<b>Début</b>", "comp 1");

			var comp2 = jcnt
					.find("table:eq(0) > tbody > tr:eq(2) > td:eq(1) > input");
			equal(comp2.val(), "15/08/2012", "comp 2");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(2) > td:eq(2) > span");
			equal(comp.html(), "<b>Responsable</b>", "comp 3");

			var comp4 = jcnt
					.find("table:eq(0) > tbody > tr:eq(2) > td:eq(3) > select");
			equal(comp4.val(), "143", "comp 4");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(2) > td:eq(4) > button");
			equal(comp.html(), "+", "comp 5");

			equal(this.mObsFactory.CallList.size(), 0, "Call A Nb :"
					+ this.mObsFactory.CallList.toString());
			comp.click();
			equal(this.mObsFactory.CallList.size(), 1, "Call B Nb :"
					+ this.mObsFactory.CallList.toString());
			var expected_cmd = "org_lucterios_task->Tasks_APAS_SelectResp(";
			expected_cmd += "isTerminate='n',task='1',";
			expected_cmd += "begin='2012-08-15',owner='143',BTN='123',end='11:30',type='o',couleur='3',rappel='5',rdv='2008-07-12 23:47',list='1;2',";
			expected_cmd += ")";
			equal(this.mObsFactory.CallList.get(0), expected_cmd, "Call #0");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(3) > td:eq(0) > span");
			equal(comp.html(), "<b>Fin</b>", "comp 6");

			var comp7 = jcnt
					.find("table:eq(0) > tbody > tr:eq(3) > td:eq(1) > span > input");
			equal(comp7.val(), "11:30", "comp 7");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(3) > td:eq(2) > span");
			equal(comp.html(), "<b>Privé</b>", "comp 8");

			var comp9 = jcnt
					.find("table:eq(0) > tbody > tr:eq(3) > td:eq(3) > input");
			equal(comp9[0].checked, true, "comp 9");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(4) > td:eq(0) > span");
			equal(comp.html(), "<b>Code couleur</b>", "comp 10");

			var comp11 = jcnt
					.find("table:eq(0) > tbody > tr:eq(4) > td:eq(1) > select");
			equal(comp11.val(), "3", "comp 11");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(4) > td:eq(2) > span");
			equal(comp.html(), "<b>Rappel (Nb de jours)</b>", "comp 12");

			var comp13 = jcnt
					.find("table:eq(0) > tbody > tr:eq(4) > td:eq(3) > span > input");
			equal(comp13.val(), "5", "comp 13");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(5) > td:eq(0) > span");
			equal(comp.html(), "<b>Date Heure RDV</b>", "comp 14");

			var comp15a = jcnt
					.find("table:eq(0) > tbody > tr:eq(5) > td:eq(1) > input:eq(1)");
			equal(comp15a.val(), "12/07/2008", "comp 15a");
			var comp15b = jcnt
					.find("table:eq(0) > tbody > tr:eq(5) > td:eq(1) > span > input");
			equal(comp15b.val(), "23:47", "comp 15b");

			var comp = jcnt
					.find("table:eq(0) > tbody > tr:eq(5) > td:eq(2) > span");
			equal(comp.html(), "<b>Listing</b>", "comp 16");

			var comp17 = jcnt
					.find("table:eq(0) > tbody > tr:eq(5) > td:eq(3) > select");
			equal(comp17.val().length, 2, "comp 17");
			equal(comp17.val()[0], "1", "comp 17a");
			equal(comp17.val()[1], "2", "comp 17b");

			var btn1 = jcnt.parent().find("div > div > button:eq(0)");
			equal(btn1.text(), 'Ok', 'btn 1');
			var btn2 = jcnt.parent().find("div > div > button:eq(1)");
			equal(btn2.text(), 'Annuler', 'btn 2');

			comp2.val('03/10/2011');
			comp4.val('0');
			comp4.change();
			comp13.val('13');
			comp15a.val('15/09/2009');
			comp17.val([ "2", "4" ]);

			btn1.click();
			ok(!gui.isExist(), "GUI exist");

			equal(this.mObsFactory.CallList.size(), 2, "Call B Nb :"
					+ this.mObsFactory.CallList.toString());
			var expected_cmd = "org_lucterios_task->Tasks_APAS_AddModifyAct(";
			expected_cmd += "isTerminate='n',task='1',";
			expected_cmd += "begin='2011-10-03',owner='0',end='11:30',type='n',couleur='3',rappel='13',rdv='2009-09-15 23:47',list='2;4',";
			expected_cmd += ")";
			equal(this.mObsFactory.CallList.get(1), expected_cmd, "Call #2");
		});

test(
		"Custom_grid",
		function() {
			var xml_receive = "<REPONSE observer='core.custom' source_extension='org_lucterios_contacts' source_action='StructureLocal'>"
					+ "<TITLE><![CDATA[Nos coordonnées]]></TITLE>"
					+ "<CONTEXT><PARAM name='personneMorale'><![CDATA[1]]></PARAM></CONTEXT>"
					+ "<COMPONENTS>	<IMAGE name='img' description=''  tab='0' x='0' y='1' colspan='1' rowspan='1' size='5544' height='64' width='64' ><TYPE><![CDATA[]]></TYPE><![CDATA[extensions/org_lucterios_contacts/images/nousContact.png]]></IMAGE>"
					+ "	<LABELFORM name='title_personne' description=''  tab='0' x='1' y='1' colspan='7' rowspan='1'><![CDATA[{[center]}{[bold]}Coordonnées de notre structure{[newline]}et de nos responsables{[/bold]}{[/center]}]]></LABELFORM>"
					+ "	<TAB name='' description=''  tab='1' x='-1' y='-1' colspan='1' rowspan='1'><![CDATA[Coordonnées]]></TAB>"
					+ "	<IMAGE name='logo' description=''  tab='1' x='5' y='1' colspan='1' rowspan='4' size='2451' height='75' width='100' ><TYPE><![CDATA[]]></TYPE><![CDATA[usr/org_lucterios_contacts/Image_100.jpg]]></IMAGE>"
					+ "	<LABELFORM name='labelraisonSociale' description=''  tab='1' x='0' y='2' colspan='1' rowspan='1'><![CDATA[{[bold]}Raison Sociale{[/bold]}]]></LABELFORM>"
					+ "	<LABEL name='raisonSociale' description='Raison+Sociale'  tab='1' x='1' y='2' colspan='3' rowspan='1'><![CDATA[Association Multi-sport de démonstration]]></LABEL>"
					+ "	<LABELFORM name='labeladresse' description=''  tab='1' x='0' y='3' colspan='1' rowspan='1'><![CDATA[{[bold]}Adresse{[/bold]}]]></LABELFORM>"
					+ "	<LABEL name='adresse' description='Adresse'  tab='1' x='1' y='3' colspan='2' rowspan='1'><![CDATA[place central]]></LABEL>"
					+ "	<LINK name='plan' description=''  tab='1' x='3' y='3' colspan='1' rowspan='1'><![CDATA[plan]]><LINK><![CDATA[http://maps.google.fr/maps?near=place+central+99000+TRIFOUILLY]]></LINK></LINK>"
					+ "	<LABELFORM name='labelcodePostal' description=''  tab='1' x='0' y='4' colspan='1' rowspan='1'><![CDATA[{[bold]}Code Postal{[/bold]}]]></LABELFORM>"
					+ "	<LABEL name='codePostal' description='Code+Postal'  tab='1' x='1' y='4' colspan='1' rowspan='1'><![CDATA[99000]]></LABEL>"
					+ "	<LABELFORM name='labelville' description=''  tab='1' x='2' y='4' colspan='1' rowspan='1'><![CDATA[{[bold]}Ville{[/bold]}]]></LABELFORM>"
					+ "	<LABEL name='ville' description='Ville'  tab='1' x='3' y='4' colspan='1' rowspan='1'><![CDATA[TRIFOUILLY]]></LABEL>"
					+ "	<LABELFORM name='labelpays' description=''  tab='1' x='0' y='5' colspan='1' rowspan='1'><![CDATA[{[bold]}Pays{[/bold]}]]></LABELFORM>"
					+ "	<LABEL name='pays' description='Pays'  tab='1' x='1' y='5' colspan='1' rowspan='1'><![CDATA[]]></LABEL>"
					+ "	<LABELFORM name='lblmail' description=''  tab='1' x='2' y='5' colspan='1' rowspan='1'><![CDATA[{[bold]}Courriel{[/bold]}]]></LABELFORM>"
					+ "	<LINK name='mail' description=''  tab='1' x='3' y='5' colspan='3' rowspan='1'><![CDATA[info@sd-libre.fr]]><LINK><![CDATA[mailto:info@sd-libre.fr]]></LINK></LINK>"
					+ "	<LABELFORM name='labelfixe' description=''  tab='1' x='0' y='6' colspan='1' rowspan='1'><![CDATA[{[bold]}Tel. Fixe{[/bold]}]]></LABELFORM>"
					+ "	<LABEL name='fixe' description='Tel.+Fixe'  tab='1' x='1' y='6' colspan='1' rowspan='1'><![CDATA[0987654321]]></LABEL>"
					+ "	<LABELFORM name='labelportable' description=''  tab='1' x='2' y='6' colspan='1' rowspan='1'><![CDATA[{[bold]}Tel. Portable{[/bold]}]]></LABELFORM>"
					+ "	<LABEL name='portable' description='Tel.+Portable'  tab='1' x='3' y='6' colspan='1' rowspan='1'><![CDATA[]]></LABEL>"
					+ "	<LABELFORM name='labelfax' description=''  tab='1' x='4' y='6' colspan='1' rowspan='1'><![CDATA[{[bold]}Fax{[/bold]}]]></LABELFORM>"
					+ "	<LABEL name='fax' description='Fax'  tab='1' x='5' y='6' colspan='1' rowspan='1'><![CDATA[]]></LABEL>"
					+ "	<LABELFORM name='labelsiren' description=''  tab='1' x='0' y='31' colspan='1' rowspan='1'><![CDATA[{[bold]}Informations légales{[/bold]}]]></LABELFORM>"
					+ "	<LABEL name='siren' description='Informations+l%E9gales'  tab='1' x='1' y='31' colspan='3' rowspan='1'><![CDATA[]]></LABEL>"
					+ "	<LABELFORM name='labelcommentaire' description=''  tab='1' x='0' y='57' colspan='1' rowspan='1'><![CDATA[{[bold]}Commentaire{[/bold]}]]></LABELFORM>"
					+ "	<LABEL name='commentaire' description='Commentaire'  tab='1' x='1' y='57' colspan='5' rowspan='1'><![CDATA[]]></LABEL>"
					+ "	<TAB name='' description=''  tab='2' x='-1' y='-1' colspan='1' rowspan='1'><![CDATA[Responsables]]></TAB>"
					+ "	<GRID name='liaison_physique' description=''  tab='2' x='0' y='32' colspan='7' rowspan='1'>"
					+ "		<HEADER name='Photo#|##getPhoto' type='icon'><![CDATA[Photo]]></HEADER>"
					+ "		<HEADER name='nom' type='str'><![CDATA[Nom]]></HEADER>"
					+ "		<HEADER name='prenom' type='str'><![CDATA[Prénom]]></HEADER>"
					+ "		<HEADER name='functions' type='str'><![CDATA[Fonctions]]></HEADER>"
					+ "		<HEADER name='allTel' type='str'><![CDATA[Téléphones]]></HEADER>"
					+ "		<HEADER name='mail' type='str'><![CDATA[Courriel]]></HEADER>"
					+ "		<RECORD id='115'>"
					+ "			<VALUE name='Photo#|##getPhoto'><![CDATA[]]></VALUE>"
					+ "			<VALUE name='nom'><![CDATA[URA]]></VALUE>"
					+ "			<VALUE name='prenom'><![CDATA[Anne]]></VALUE>"
					+ "			<VALUE name='functions'><![CDATA[Président]]>"
					+ "			</VALUE><VALUE name='allTel'><![CDATA[0748456889{[newline]}0006034645]]></VALUE>"
					+ "			<VALUE name='mail'><![CDATA[anne626@free.fr]]></VALUE>"
					+ "		</RECORD>"
					+ "		<RECORD id='138'>"
					+ "			<VALUE name='Photo#|##getPhoto'><![CDATA[usr/org_lucterios_contacts/Image_101.jpg]]></VALUE>"
					+ "			<VALUE name='nom'><![CDATA[EVEFAZOB]]></VALUE>"
					+ "			<VALUE name='prenom'><![CDATA[Raphael]]></VALUE>"
					+ "			<VALUE name='functions'><![CDATA[Trésorier]]></VALUE>"
					+ "			<VALUE name='allTel'><![CDATA[0673726055{[newline]}0546369191]]></VALUE>"
					+ "			<VALUE name='mail'><![CDATA[raphael205@orange.fr]]></VALUE>"
					+ "		</RECORD>"
					+ "		<RECORD id='110'>"
					+ "			<VALUE name='Photo#|##getPhoto'><![CDATA[]]></VALUE>"
					+ "			<VALUE name='nom'><![CDATA[GACIGO]]></VALUE>"
					+ "			<VALUE name='prenom'><![CDATA[Michel]]></VALUE>"
					+ "			<VALUE name='functions'><![CDATA[Secrétaire]]></VALUE>"
					+ "			<VALUE name='allTel'><![CDATA[0728886808{[newline]}0714458478]]></VALUE>"
					+ "			<VALUE name='mail'><![CDATA[michel387@free.fr]]></VALUE>"
					+ "		</RECORD>"
					+ "		<ACTIONS>"
					+ "			<ACTION icon='images/edit.png' sizeicon='787' extension='org_lucterios_contacts' action='liaison_APAS_Fiche' close='0' modal='1' unique='0'><![CDATA[_Editer]]></ACTION>"
					+ "			<ACTION icon='images/add.png' sizeicon='487' extension='org_lucterios_contacts' action='liaison_APAS_AddSearch' close='0' modal='1' unique='1'><![CDATA[_Rechercher/Ajouter]]></ACTION>"
					+ "		</ACTIONS>"
					+ "		</GRID>"
					+ "	<LABELFORM name='nbresponsable' description=''  tab='2' x='0' y='33' colspan='1' rowspan='1'><![CDATA[Nombre de responsables : 3]]></LABELFORM>"
					+ "	<LINK name='email' description=''  tab='2' x='1' y='33' colspan='1' rowspan='1'><![CDATA[Ecrire a tous]]><LINK><![CDATA[mailto:anne626@free.fr,raphael205@orange.fr,michel387@free.fr]]></LINK></LINK>"
					+ "</COMPONENTS>"
					+ "<ACTIONS>"
					+ "	<ACTION icon='images/edit.png' sizeicon='787' extension='org_lucterios_contacts' action='personneMorale_APAS_AddModify' close='0' modal='1'><![CDATA[_Modifier]]></ACTION>"
					+ "	<ACTION icon='images/print.png' sizeicon='676' extension='org_lucterios_contacts' action='ImpressionLocal' close='0' modal='1'><![CDATA[_Imprimer]]></ACTION>"
					+ "	<ACTION icon='images/close.png' sizeicon='921' close='1' modal='1'><![CDATA[_Fermer]]></ACTION>"
					+ "</ACTIONS>" + "</REPONSE>";

			var parse = xml_receive.parseXML();
			var obs = new ObserverCustom();
			obs.setSource("org_lucterios_contacts", "StructureLocal");
			obs.setContent(parse);
			obs.show("Nos coordonées", FORM_MODAL);

			var gui = obs.getGUI();
			ok(gui != null, "getGUI");
			ok(gui.isExist(), "GUI exist");
			var jcnt = gui.getHtmlDom();

			var table_comp = jcnt
					.find("div > div:eq(1) > table:eq(0) > tbody > tr:eq(0) > td:eq(0) > table:eq(0)");
			var table_content = table_comp.find("tbody > tr:eq(0) > td:eq(0)");
			var table_buttons = table_comp.find("tbody > tr:eq(0) > td:eq(1)");

			var comp = table_content
					.find("table:eq(0) > thead > tr:eq(0) > th:eq(1)");
			equal(comp.html(), "Nom", "head 1");

			var comp = table_content
					.find("table:eq(0) > thead > tr:eq(0) > th:eq(4)");
			equal(comp.html(), "Téléphones", "head 2");

			var cell1 = table_content
					.find("table:eq(0) > tbody > tr:eq(0) > td:eq(2)");
			equal(cell1.html(), "Anne", "cell 1");

			var cell2 = table_content
					.find("table:eq(0) > tbody > tr:eq(1) > td:eq(0) > img:eq(0)");
			equal(cell2.attr("src"),
					"STUB/usr/org_lucterios_contacts/Image_101.jpg",
					"cell 2");

			var cell3 = table_content
					.find("table:eq(0) > tbody > tr:eq(2) > td:eq(4)");
			equal(cell3.html(), "0728886808<br>0714458478", "cell 3");

			var btn1 = table_buttons.find('button:eq(0)');
			equal(btn1.text(), 'Editer', 'btn 1');
			equal(btn1.prop("disabled"), true, 'btn 1 dis');
			var btn2 = table_buttons.find('button:eq(1)');
			equal(btn2.text(), 'Rechercher/Ajouter', 'btn 2');
			equal(btn2.prop("disabled"), false, 'btn 2 dis');

			var row1 = table_content.find("table:eq(0) > tbody > tr:eq(0)");
			equal(row1.hasClass("selected"), false, 'row 1');
			var row2 = table_content.find("table:eq(0) > tbody > tr:eq(1)");
			equal(row2.hasClass("selected"), false, 'row 2');
			var row3 = table_content.find("table:eq(0) > tbody > tr:eq(2)");
			equal(row3.hasClass("selected"), false, 'row 3');

			row2.click();
			equal(btn1.prop("disabled"), false, 'btn 1 dis');
			equal(btn2.prop("disabled"), false, 'btn 2 dis');
			equal(row1.hasClass("selected"), false, 'row 1:'
					+ row1.attr('class'));
			equal(row2.hasClass("selected"), true, 'row 2:'
					+ row2.attr('class'));
			equal(row3.hasClass("selected"), false, 'row 3:'
					+ row3.attr('class'));

			row1.click();
			equal(btn1.prop("disabled"), false, 'btn 1 dis');
			equal(btn2.prop("disabled"), false, 'btn 2 dis');
			equal(row1.hasClass("selected"), true, 'row 1:'
					+ row1.attr('class'));
			equal(row2.hasClass("selected"), false, 'row 2:'
					+ row2.attr('class'));
			equal(row3.hasClass("selected"), false, 'row 3:'
					+ row3.attr('class'));

			row1.click();
			equal(btn1.prop("disabled"), true, 'btn 1 dis');
			equal(btn2.prop("disabled"), false, 'btn 2 dis');
			equal(row1.hasClass("selected"), false, 'row 1:'
					+ row1.attr('class'));
			equal(row2.hasClass("selected"), false, 'row 2:'
					+ row2.attr('class'));
			equal(row3.hasClass("selected"), false, 'row 3:'
					+ row3.attr('class'));

			equal(this.mObsFactory.CallList.size(), 0, "Call A Nb :"
					+ this.mObsFactory.CallList.toString());

			btn2.click();
			equal(this.mObsFactory.CallList.size(), 1, "Call B Nb :"
					+ this.mObsFactory.CallList.toString());
			var expected_cmd = "org_lucterios_contacts->liaison_APAS_AddSearch(";
			expected_cmd += "personneMorale='1',";
			expected_cmd += ")";
			equal(this.mObsFactory.CallList.get(0), expected_cmd, "Call #0");

			row3.click();
			equal(btn1.prop("disabled"), false, 'btn 1 dis');
			equal(btn2.prop("disabled"), false, 'btn 2 dis');
			equal(row1.hasClass("selected"), false, 'row 1:'
					+ row1.attr('class'));
			equal(row2.hasClass("selected"), false, 'row 2:'
					+ row2.attr('class'));
			equal(row3.hasClass("selected"), true, 'row 3:'
					+ row3.attr('class'));

			btn1.click();
			equal(this.mObsFactory.CallList.size(), 2, "Call C Nb :"
					+ this.mObsFactory.CallList.toString());
			var expected_cmd = "org_lucterios_contacts->liaison_APAS_Fiche(";
			expected_cmd += "personneMorale='1',";
			expected_cmd += "liaison_physique='110',";
			expected_cmd += ")";
			equal(this.mObsFactory.CallList.get(1), expected_cmd, "Call #0");

			gui.close();
			ok(!gui.isExist(), "GUI exist");

			equal(this.mObsFactory.CallList.size(), 2, "Call D Nb :"
					+ this.mObsFactory.CallList.toString());
		});

test(
		"Custom_need",
		function() {
			var xml_receive = "<REPONSE observer='core.custom' source_extension='org_lucterios_contacts' source_action='personnePhysique_APAS_AddModify'>"
					+ "<TITLE><![CDATA[Ajouter une personne physique]]></TITLE>"
					+ "<CONTEXT></CONTEXT>"
					+ "<COMPONENTS>	<IMAGE name='img' description=''  tab='0' x='1' y='0' colspan='1' rowspan='3' size='3618' height='64' width='64' ><TYPE><![CDATA[]]></TYPE><![CDATA[extensions/org_lucterios_contacts/images/contactPhyique.png]]></IMAGE>"
					+ "	<LABELFORM name='labelsexe' description='labelsexe'  tab='0' x='2' y='0' colspan='1' rowspan='1' needed='1'><![CDATA[{[bold]}Civilité{[/bold]}]]></LABELFORM>"
					+ "	<SELECT name='sexe' description='Civilit%E9'  tab='0' x='3' y='0' colspan='1' rowspan='1' VMin='20' HMin='150' needed='1'><CASE id='0'><![CDATA[Monsieur]]></CASE><CASE id='1'><![CDATA[Madame/Mademoiselle]]></CASE><ACTIONS></ACTIONS></SELECT>"
					+ "	<LABELFORM name='labelnom' description=''  tab='0' x='2' y='1' colspan='1' rowspan='1'><![CDATA[{[bold]}Nom{[/bold]}]]></LABELFORM>"
					+ "	<EDIT name='nom' description='Nom'  tab='0' x='3' y='1' colspan='1' rowspan='1' VMin='20' HMin='150' needed='1'><![CDATA[]]><ACTIONS></ACTIONS></EDIT>"
					+ "	<LABELFORM name='labelprenom' description=''  tab='0' x='4' y='1' colspan='1' rowspan='1'><![CDATA[{[bold]}Prénom{[/bold]}]]></LABELFORM>"
					+ "	<EDIT name='prenom' description='Pr%E9nom'  tab='0' x='5' y='1' colspan='1' rowspan='1' VMin='20' HMin='150' needed='1'><![CDATA[]]><ACTIONS></ACTIONS></EDIT>"
					+ "	<LABELFORM name='labeladresse' description=''  tab='0' x='2' y='2' colspan='1' rowspan='1'><![CDATA[{[bold]}Adresse{[/bold]}]]></LABELFORM>"
					+ "	<MEMO name='adresse' description='Adresse'  tab='0' x='3' y='2' colspan='3' rowspan='1' VMin='50' HMin='200' needed='1' FirstLine='-1'><![CDATA[]]><ACTIONS></ACTIONS></MEMO>"
					+ "	<LABELFORM name='labelcodePostal' description=''  tab='0' x='2' y='3' colspan='1' rowspan='1'><![CDATA[{[bold]}Code Postal{[/bold]}]]></LABELFORM>"
					+ "	<EDIT name='codePostal' description='Code+Postal'  tab='0' x='3' y='3' colspan='1' rowspan='1' VMin='20' HMin='150' needed='1'><![CDATA[]]><ACTIONS><ACTION extension='org_lucterios_contacts' action='personnePhysique_APAS_AddModify' close='0' modal='2' unique='1'><![CDATA[Modifier]]></ACTION></ACTIONS></EDIT>"
					+ "	<LABELFORM name='lblville' description=''  tab='0' x='4' y='3' colspan='1' rowspan='1'><![CDATA[{[bold]}Ville{[/bold]}]]></LABELFORM>"
					+ "	<EDIT name='ville' description=''  tab='0' x='5' y='3' colspan='1' rowspan='1' VMin='20' HMin='150'><![CDATA[]]><ACTIONS></ACTIONS></EDIT>"
					+ "	<LABELFORM name='labelpays' description=''  tab='0' x='2' y='4' colspan='1' rowspan='1'><![CDATA[{[bold]}Pays{[/bold]}]]></LABELFORM>"
					+ "	<EDIT name='pays' description='Pays'  tab='0' x='3' y='4' colspan='1' rowspan='1' VMin='20' HMin='150'><![CDATA[]]><ACTIONS></ACTIONS></EDIT>"
					+ "	<LABELFORM name='labelfixe' description=''  tab='0' x='2' y='5' colspan='1' rowspan='1'><![CDATA[{[bold]}Tel. Fixe{[/bold]}]]></LABELFORM>"
					+ "	<EDIT name='fixe' description='Tel.+Fixe'  tab='0' x='3' y='5' colspan='1' rowspan='1' VMin='20' HMin='150'><![CDATA[]]><ACTIONS></ACTIONS></EDIT>"
					+ "	<LABELFORM name='labelportable' description=''  tab='0' x='4' y='5' colspan='1' rowspan='1'><![CDATA[{[bold]}Tel. Portable{[/bold]}]]></LABELFORM>"
					+ "	<EDIT name='portable' description='Tel.+Portable'  tab='0' x='5' y='5' colspan='1' rowspan='1' VMin='20' HMin='150'><![CDATA[]]><ACTIONS></ACTIONS></EDIT>"
					+ "	<LABELFORM name='labelfax' description=''  tab='0' x='2' y='6' colspan='1' rowspan='1'><![CDATA[{[bold]}Fax{[/bold]}]]></LABELFORM>"
					+ "	<EDIT name='fax' description='Fax'  tab='0' x='3' y='6' colspan='1' rowspan='1' VMin='20' HMin='150'><![CDATA[]]><ACTIONS></ACTIONS></EDIT>"
					+ "	<LABELFORM name='labelmail' description=''  tab='0' x='2' y='7' colspan='1' rowspan='1'><![CDATA[{[bold]}Courriel{[/bold]}]]></LABELFORM>"
					+ "	<EDIT name='mail' description='Courriel'  tab='0' x='3' y='7' colspan='3' rowspan='1'><![CDATA[]]><ACTIONS></ACTIONS></EDIT>"
					+ "	<LABELFORM name='labelcommentaire' description=''  tab='0' x='2' y='50' colspan='1' rowspan='1'><![CDATA[{[bold]}Commentaire{[/bold]}]]></LABELFORM>"
					+ "	<MEMO name='commentaire' description='Commentaire'  tab='0' x='3' y='50' colspan='3' rowspan='1' VMin='50' HMin='200' FirstLine='-1'><![CDATA[]]><ACTIONS></ACTIONS></MEMO>"
					+ "	<LABELFORM name='Lbl_uploadlogo' description=''  tab='0' x='2' y='51' colspan='1' rowspan='1'><![CDATA[{[bold]}Image{[/bold]}]]></LABELFORM>"
					+ "	<UPLOAD name='uploadlogo' description=''  tab='0' x='3' y='51' colspan='3' rowspan='1' maxsize='1048576'><![CDATA[]]><FILTER><![CDATA[.jpg]]></FILTER><FILTER><![CDATA[.gif]]></FILTER><FILTER><![CDATA[.png]]></FILTER><FILTER><![CDATA[.bmp]]></FILTER></UPLOAD>"
					+ "	<LABELFORM name='Lbl_warning' description=''  tab='0' x='2' y='52' colspan='4' rowspan='1'><![CDATA[{[center]}{[italic]}{[font size='-2']}Importer de préférence une image JPEG de 100x100 pts.{[/font]}{[/italic]}{[/center]}]]></LABELFORM>"
					+ "</COMPONENTS>"
					+ "<ACTIONS>"
					+ "	<ACTION icon='images/ok.png' sizeicon='1731' extension='org_lucterios_contacts' action='personnePhysique_APAS_AddModifyAct' close='1' modal='1'><![CDATA[_Ok]]></ACTION>"
					+ "   <ACTION icon='images/cancel.png' sizeicon='1656'><![CDATA[_Annuler]]></ACTION>"
					+ "</ACTIONS>"
					+ "<CLOSE_ACTION><ACTION extension='CORE' action='UNLOCK' close='1' modal='1' unique='1'><![CDATA[unlock]]></ACTION></CLOSE_ACTION>"
					+ "</REPONSE>";

			var message_dlg = null;
			showMessageDialog = function(aText, aTitle) {
				message_dlg = aText;
			}

			var parse = xml_receive.parseXML();
			var obs = new ObserverCustom();
			obs.setSource("org_lucterios_contacts",
					"personnePhysique_APAS_AddModify");
			obs.setContent(parse);
			obs.show("Ajouter", FORM_MODAL);

			var gui = obs.getGUI();
			ok(gui != null, "getGUI");
			ok(gui.isExist(), "GUI exist");
			var jcnt = gui.getHtmlDom();

			var comp = jcnt.find("table > tbody > tr > td > input[name='nom']");
			equal(comp.val(), "", "comp Nom");
			comp.focus();
			comp.val("DUPOND");

			var btn1 = jcnt.parent().find("div > div > button:eq(0)");
			equal(btn1.text(), 'Ok', 'btn 1');
			var btn2 = jcnt.parent().find("div > div > button:eq(1)");
			equal(btn2.text(), 'Annuler', 'btn 2');

			equal(this.mObsFactory.CallList.size(), 0, "Call A Nb :"
					+ this.mObsFactory.CallList.toString());
			equal(message_dlg, null);
			btn1.click();
			equal(message_dlg, "Le champ 'Prénom' est obligatoire!");

			equal(this.mObsFactory.CallList.size(), 0, "Call B Nb :"
					+ this.mObsFactory.CallList.toString());

			var comp = jcnt
					.find("table > tbody > tr > td > input[name='prenom']");
			comp.val("Jean");
			var comp = jcnt
					.find("table > tbody > tr > td > textarea[name='adresse']");
			comp.val("1 rue de la paix");
			var comp = jcnt
					.find("table > tbody > tr > td > input[name='codePostal']");
			comp.val("12300");
			var comp = jcnt
					.find("table > tbody > tr > td > input[name='Ville']");
			comp.val("TRUC");
			btn1.click();
			equal(this.mObsFactory.CallList.size(), 2, "Call C Nb :"
					+ this.mObsFactory.CallList.toString());

			ok(!gui.isExist(), "GUI exist");
			var expected_cmd = "org_lucterios_contacts->personnePhysique_APAS_AddModifyAct(";
			expected_cmd += "sexe='0',nom='DUPOND',prenom='Jean',adresse='1 rue de la paix',codePostal='12300',ville='',pays='',fixe='',portable='',fax='',mail='',commentaire='',";
			expected_cmd += ")";
			equal(this.mObsFactory.CallList.get(1), expected_cmd, "Call #1");
		});
