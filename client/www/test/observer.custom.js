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

test("Custom_Simple", function() {
	var json_receive = {
		"actions" : [],
		"context" : {},
		"close" : null,
		"data" : {
			"dummytitle" : "Dummy",
			"dummy_time" : "2017-10-26T19:42:12.033"
		},
		"meta" : {
			"action" : "statusMenu",
			"title" : "R\u00e9sum\u00e9",
			"extension" : "CORE",
			"observer" : "core.custom"
		},
		"comp" : [ {
			"description" : "",
			"y" : 0,
			"needed" : false,
			"x" : 0,
			"component" : "LABELFORM",
			"rowspan" : 1,
			"name" : "dummytitle",
			"tab" : 0,
			"colspan" : 4,
			"formatstr" : "{[center]}{[u]}{[b]}{0}{[/b]}{[/u]}{[/center]}",
			"formatnum" : null
		}, {
			"description" : "",
			"y" : 1,
			"needed" : false,
			"x" : 0,
			"component" : "LABELFORM",
			"rowspan" : 1,
			"name" : "dummy_time",
			"tab" : 0,
			"colspan" : 4,
			"formatstr" : "{[center]}{[font color=\"blue\"]}{0}{[/font]}{[/center]}",
			"formatnum" : "H"
		} ]
	};

	var obs = new ObserverCustom();
	obs.setSource("CORE", "statusMenu");
	obs.setContent(json_receive);
	obs.show("Résumé", FORM_MODAL);

	var gui = obs.getGUI();
	ok(gui != null, "getGUI");
	ok(gui.isExist(), "GUI exist");
	var jcnt = gui.getHtmlDom();

	var lbl = jcnt.find("table:eq(0) > tbody > tr:eq(0) > td:eq(0) > lct-cell > span");
	equal(lbl.html(), "<center><u><b>Dummy</b></u></center>", "text 1");

	var lbl = jcnt.find("table:eq(0) > tbody > tr:eq(1) > td:eq(0) > lct-cell > span");
	equal(lbl.html(), "<center><font color=\"blue\">jeudi 26 octobre 2017 à 19:42</font></center>", "text 2");

	var btn1 = jcnt.parent().find("div:eq(2) > div:eq(0) > button:eq(0)");
	equal(btn1.text(), 'Fermer', 'btn 1');
	var btn2 = jcnt.parent().find("div:eq(2) > div:eq(0) > button:eq(1)");
	equal(btn2.text(), '', 'btn 2');

	obs.close();
	ok(!gui.isExist(), "GUI exist");
	equal(this.mObsFactory.CallList.size(), 0, "Call Nb");
});

test(
		"Custom_EditMemo",
		function() {
			var json_receive = {
				"context" : {
					"LOCK_IDENT" : "lucterios.contacts.models-LegalEntity-1"
				},
				"comp" : [ {
					"y" : 0,
					"rowspan" : 6,
					"colspan" : 1,
					"type" : "",
					"component" : "IMAGE",
					"name" : "img",
					"needed" : false,
					"description" : "",
					"tab" : 0,
					"x" : 0
				}, {
					"action" : null,
					"colspan" : 2,
					"is_default" : false,
					"rowspan" : 1,
					"description" : "nom",
					"tab" : 0,
					"size" : 100,
					"is_mini" : false,
					"y" : 0,
					"name" : "name",
					"reg_expr" : "",
					"component" : "EDIT",
					"javascript" : "",
					"needed" : true,
					"x" : 1
				}, {
					"action" : null,
					"submenu" : [],
					"colspan" : 2,
					"is_default" : false,
					"rowspan" : 1,
					"description" : "adresse",
					"tab" : 0,
					"x" : 1,
					"y" : 2,
					"name" : "address",
					"HMin" : 200,
					"component" : "MEMO",
					"javascript" : "",
					"needed" : true,
					"is_mini" : false,
					"with_hypertext" : false,
					"VMin" : 50
				}, {
					"action" : {
						"id" : "postal_code",
						"action" : "currentStructureAddModify",
						"extension" : "lucterios.contacts",
						"text" : "",
						"modal" : "2",
						"params" : null,
						"close" : "0",
						"icon" : "/static/lucterios.contacts/images/ourDetails.png",
						"unique" : "1",
						"name" : "postal_code"
					},
					"colspan" : 1,
					"is_default" : false,
					"rowspan" : 1,
					"description" : "code postal",
					"tab" : 0,
					"size" : 10,
					"is_mini" : false,
					"y" : 3,
					"name" : "postal_code",
					"reg_expr" : "",
					"component" : "EDIT",
					"javascript" : "",
					"needed" : true,
					"x" : 1
				}, {
					"action" : null,
					"colspan" : 1,
					"is_default" : false,
					"rowspan" : 1,
					"description" : "ville",
					"tab" : 0,
					"size" : 100,
					"is_mini" : false,
					"y" : 3,
					"name" : "city",
					"reg_expr" : "",
					"component" : "EDIT",
					"javascript" : "",
					"needed" : true,
					"x" : 2
				}, {
					"action" : null,
					"colspan" : 2,
					"is_default" : false,
					"rowspan" : 1,
					"description" : "pays",
					"tab" : 0,
					"size" : 100,
					"is_mini" : false,
					"y" : 4,
					"name" : "country",
					"reg_expr" : "",
					"component" : "EDIT",
					"javascript" : "",
					"needed" : false,
					"x" : 1
				}, {
					"action" : null,
					"colspan" : 1,
					"is_default" : false,
					"rowspan" : 1,
					"description" : "tel1",
					"tab" : 0,
					"size" : 20,
					"is_mini" : false,
					"y" : 5,
					"name" : "tel1",
					"reg_expr" : "",
					"component" : "EDIT",
					"javascript" : "",
					"needed" : false,
					"x" : 1
				}, {
					"action" : null,
					"colspan" : 1,
					"is_default" : false,
					"rowspan" : 1,
					"description" : "tel2",
					"tab" : 0,
					"size" : 20,
					"is_mini" : false,
					"y" : 5,
					"name" : "tel2",
					"reg_expr" : "",
					"component" : "EDIT",
					"javascript" : "",
					"needed" : false,
					"x" : 2
				}, {
					"action" : null,
					"colspan" : 2,
					"is_default" : false,
					"rowspan" : 1,
					"description" : "courriel",
					"tab" : 0,
					"size" : 254,
					"is_mini" : false,
					"y" : 6,
					"name" : "email",
					"reg_expr" : "",
					"component" : "EDIT",
					"javascript" : "",
					"needed" : false,
					"x" : 1
				}, {
					"action" : null,
					"submenu" : [],
					"colspan" : 2,
					"is_default" : false,
					"rowspan" : 1,
					"description" : "commentaire",
					"tab" : 0,
					"x" : 1,
					"y" : 7,
					"name" : "comment",
					"HMin" : 200,
					"component" : "MEMO",
					"javascript" : "",
					"needed" : false,
					"is_mini" : false,
					"with_hypertext" : false,
					"VMin" : 50
				}, {
					"action" : null,
					"submenu" : [],
					"colspan" : 2,
					"is_default" : false,
					"rowspan" : 1,
					"description" : "N\u00b0 SIRET/SIREN",
					"tab" : 0,
					"x" : 1,
					"y" : 8,
					"name" : "identify_number",
					"HMin" : 200,
					"component" : "MEMO",
					"javascript" : "",
					"needed" : false,
					"is_mini" : false,
					"with_hypertext" : false,
					"VMin" : 50
				}, {
					"action" : null,
					"colspan" : 1,
					"is_default" : false,
					"rowspan" : 1,
					"description" : "text",
					"tab" : 0,
					"size" : -1,
					"is_mini" : false,
					"y" : 13,
					"name" : "custom_1",
					"reg_expr" : "",
					"component" : "EDIT",
					"javascript" : "",
					"needed" : false,
					"x" : 1
				}, {
					"action" : null,
					"min" : 1.0,
					"colspan" : 2,
					"is_default" : false,
					"rowspan" : 1,
					"description" : "numero",
					"tab" : 0,
					"prec" : 0,
					"is_mini" : false,
					"y" : 13,
					"name" : "custom_2",
					"component" : "FLOAT",
					"javascript" : "",
					"needed" : true,
					"max" : 100.0,
					"x" : 2
				}, {
					"action" : null,
					"colspan" : 1,
					"case" : [ [ 0, "bb" ], [ 1, "dd" ], [ 2, "aa" ], [ 3, "cc" ] ],
					"is_default" : false,
					"rowspan" : 1,
					"description" : "choix",
					"tab" : 0,
					"is_mini" : false,
					"y" : 14,
					"name" : "custom_4",
					"component" : "SELECT",
					"javascript" : "",
					"needed" : false,
					"x" : 1
				}, {
					"action" : null,
					"colspan" : 2,
					"is_default" : false,
					"rowspan" : 1,
					"description" : "Sur?",
					"tab" : 0,
					"is_mini" : false,
					"y" : 14,
					"name" : "custom_5",
					"component" : "CHECK",
					"javascript" : "",
					"needed" : false,
					"x" : 2
				} ],
				"close" : {
					"id" : "CORE/unlock",
					"action" : "unlock",
					"text" : "unlock",
					"modal" : "1",
					"params" : null,
					"close" : "1",
					"extension" : "CORE",
					"unique" : "1"
				},
				"meta" : {
					"action" : "currentStructureAddModify",
					"title" : "Nos coordonn\u00e9es",
					"extension" : "lucterios.contacts",
					"observer" : "core.custom"
				},
				"data" : {
					"tel2" : "",
					"comment" : "",
					"img" : "/static/lucterios.contacts/images/ourDetails.png",
					"name" : "Association Multi-sport de d\u00e9monstration",
					"email" : "info@sd-libre.fr",
					"custom_5" : 0,
					"tel1" : "0987654321",
					"address" : "place central",
					"identify_number" : "",
					"custom_1" : "",
					"custom_2" : 0,
					"city" : "TRIFOUILLY",
					"uploadlogo" : "",
					"postal_code" : "99000",
					"country" : "",
					"custom_4" : 0
				},
				"actions" : [ {
					"id" : "lucterios.contacts/currentStructureAddModify",
					"action" : "currentStructureAddModify",
					"extension" : "lucterios.contacts",
					"text" : "Ok",
					"modal" : "1",
					"params" : {
						"SAVE" : "YES"
					},
					"close" : "1",
					"icon" : "/static/lucterios.CORE/images/ok.png",
					"unique" : "1"
				}, {
					"id" : "",
					"modal" : "1",
					"text" : "Annuler",
					"params" : null,
					"close" : "1",
					"icon" : "/static/lucterios.CORE/images/cancel.png",
					"unique" : "1"
				} ]
			};
			var obs = new ObserverCustom();
			obs.setSource("lucterios.contacts", "currentStructureAddModify");
			obs.setContent(json_receive);
			obs.show("Nos coordonnées", FORM_MODAL);

			var gui = obs.getGUI();
			ok(gui != null, "getGUI");
			ok(gui.isExist(), "GUI exist");
			var jcnt = gui.getHtmlDom();

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(0) > td:eq(0) > lct-cell > img");
			var img = comp.attr("src");
			equal(img.substring(0, img.indexOf('=')), "STUB//static/lucterios.contacts/images/ourDetails.png?val", "comp 1");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(0) > td:eq(1) > lct-cell > label");
			equal(comp.html(), "nom", "comp 2");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(0) > td:eq(1) > lct-cell > lct-ctrl > input");
			equal(comp.val(), "Association Multi-sport de démonstration", "comp 3");
			comp.focus();
			comp.val("AAA");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0) > lct-cell > label");
			equal(comp.html(), "adresse", "comp 4");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0) > lct-cell > lct-ctrl > textarea");
			equal(comp.text(), "place central", "comp 5");
			comp.focus();
			comp.text("BBB\nCCC");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(3) > td:eq(0) > lct-cell > label");
			equal(comp.html(), "code postal", "comp 6");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(3) > td:eq(0) > lct-cell > lct-ctrl > input");
			equal(comp.val(), "99000", "comp 7");
			comp.focus();
			comp.val("123456");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(3) > td:eq(1) > lct-cell > label");
			equal(comp.html(), "ville", "comp 8");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(3) > td:eq(1) > lct-cell > lct-ctrl > input");
			equal(comp.val(), "TRIFOUILLY", "comp 9");
			comp.focus();
			comp.val("DDDD");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(4) > td:eq(0) > lct-cell > label");
			equal(comp.html(), "pays", "comp 10");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(4) > td:eq(0) > lct-cell > lct-ctrl > input");
			equal(comp.val(), "", "comp 11");
			comp.focus();
			comp.val("EEEE");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(5) > td:eq(0) > lct-cell > label");
			equal(comp.html(), "tel1", "comp 12");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(5) > td:eq(0) > lct-cell > lct-ctrl > input");
			equal(comp.val(), "0987654321", "comp 13");
			comp.focus();
			comp.val("FFFFF");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(5) > td:eq(1) > lct-cell > label");
			equal(comp.html(), "tel2", "comp 14");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(5) > td:eq(1) > lct-cell > lct-ctrl > input");
			equal(comp.val(), "", "comp 15");
			comp.focus();
			comp.val("GGGGG");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(6) > td:eq(1) > lct-cell > label");
			equal(comp.html(), "courriel", "comp 18");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(6) > td:eq(1) > lct-cell > lct-ctrl > input");
			equal(comp.val(), "info@sd-libre.fr", "comp 19");
			comp.focus();
			comp.val("IIIII");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(7) > td:eq(1) > lct-cell > label");
			equal(comp.html(), "commentaire", "comp 22");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(7) > td:eq(1) > lct-cell > lct-ctrl > textarea");
			equal(comp.text(), "", "comp 23");
			comp.focus();
			comp.text("LL\nMMMM\nNN");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(8) > td:eq(1) > lct-cell > label");
			equal(comp.html(), "N° SIRET/SIREN", "comp 20");

			var comp = jcnt.find("table:eq(0) > tbody > tr:eq(8) > td:eq(1) > lct-cell > lct-ctrl > textarea");
			equal(comp.text(), "", "comp 21");
			comp.focus();
			comp.text("JJ\nKKKK");

			var btn1 = jcnt.parent().find("div:eq(2) > div:eq(0) > button:eq(0)");
			equal(btn1.text(), 'Ok', 'btn 1');
			var btn2 = jcnt.parent().find("div:eq(2) > div:eq(0) > button:eq(1)");
			equal(btn2.text(), 'Annuler', 'btn 2');

			this.mObsFactory.init();

			equal(this.mObsFactory.CallList.size(), 0, "Call A null :" + this.mObsFactory.CallList.toString());

			btn1.click();

			ok(!gui.isExist(), "GUI exist");
			equal(this.mObsFactory.CallList.size(), 2, "Call B Nb :" + this.mObsFactory.CallList.toString());
			var expected_cmd = "CORE->unlock(LOCK_IDENT='lucterios.contacts.models-LegalEntity-1',)";
			equal(this.mObsFactory.CallList.get(0), expected_cmd, "Call #1");
			var expected_cmd = "lucterios.contacts->currentStructureAddModify(LOCK_IDENT='lucterios.contacts.models-LegalEntity-1',name='AAA',address='BBB{[br/]}CCC',postal_code='123456',city='DDDD',country='EEEE',tel1='FFFFF',tel2='GGGGG',email='IIIII',comment='LL{[br/]}MMMM{[br/]}NN',identify_number='JJ{[br/]}KKKK',custom_1='',custom_2='1',custom_4='0',custom_5='n',SAVE='YES',)";
			equal(this.mObsFactory.CallList.get(1), expected_cmd, "Call #2");
		});

asyncTest("Custom_Upload", function() {
	var json_receive = {
		"meta" : {
			"action" : "documentAddModify",
			"title" : "Ajouter un document",
			"observer" : "core.custom",
			"extension" : "lucterios.documents"
		},
		"actions" : [ {
			"text" : "Ok",
			"params" : {
				"SAVE" : "YES"
			},
			"icon" : "/static/lucterios.CORE/images/ok.png",
			"modal" : "1",
			"unique" : "1",
			"id" : "lucterios.documents/documentAddModify",
			"action" : "documentAddModify",
			"close" : "1",
			"extension" : "lucterios.documents"
		}, {
			"text" : "Annuler",
			"icon" : "/static/lucterios.CORE/images/cancel.png",
			"modal" : "1",
			"unique" : "1",
			"id" : "",
			"params" : null,
			"close" : "1"
		} ],
		"comp" : [ {
			"tab" : 0,
			"needed" : false,
			"filter" : [ '.jpg', '.png', '.gif' ],
			"maxsize" : 16777216,
			"component" : "UPLOAD",
			"description" : "",
			"x" : 1,
			"compress" : true,
			"rowspan" : 1,
			"y" : 1,
			"name" : "filename",
			"colspan" : 1,
			"http_file" : true
		}, {
			"HMin" : 200,
			"tab" : 0,
			"needed" : true,
			"VMin" : 50,
			"component" : "MEMO",
			"description" : "description",
			"javascript" : "",
			"is_mini" : false,
			"is_default" : false,
			"submenu" : [],
			"x" : 1,
			"action" : null,
			"rowspan" : 1,
			"with_hypertext" : false,
			"y" : 2,
			"name" : "description",
			"colspan" : 1
		} ],
		"data" : {
			"description" : "",
			"filename" : ""
		},
		"context" : {},
		"close" : null
	}
	var content_file = 'This file is part of Diacamma, a software developped by "Le Sanglier du Libre" (http://www.sd-libre.fr)\n'
			+ 'Thanks to have payed a retribution for using this module.\n' + '\n'
			+ 'Diacamma is free software; you can redistribute it and/or modify\n'
			+ 'it under the terms of the GNU General Public License as published by\n'
			+ 'the Free Software Foundation; either version 2 of the License, or\n' + '(at your option) any later version.\n' + '\n'
			+ 'Diacamma is distributed in the hope that it will be useful,\n' + 'but WITHOUT ANY WARRANTY; without even the implied warranty of\n'
			+ 'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n' + 'GNU General Public License for more details.\n' + '\n'
			+ 'You should have received a copy of the GNU General Public License\n' + 'along with Lucterios; if not, write to the Free Software\n'
			+ 'Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA';

	var obs = new ObserverCustom();
	obs.setSource("lucterios.documents", "documentAddModify");
	obs.setContent(json_receive);
	obs.show("Ajouter un document", FORM_MODAL);

	obs.mCompList.get('filename').getValue = function() {
		var blob_content;
		if (typeof (Blob) === typeof (Function)) {
			blob_content = new Blob([ content_file ], {
				type : "text/plain;charset=UTF-8"
			});
		} else {
			var builder = new WebKitBlobBuilder();
			builder.append(content_file);
			blob_content = builder.getBlob();
		}
		blob_content.name = 'undefined';
		return blob_content;
	};

	var gui = obs.getGUI();
	ok(gui != null, "getGUI");
	ok(gui.isExist(), "GUI exist");
	var jcnt = gui.getHtmlDom();

	var comp = jcnt.find("table:eq(0) > tbody > tr:eq(0) > td:eq(1) > lct-cell > div > input");
	equal(comp.attr("accept"), ".jpg,.png,.gif", "comp upload");
	comp.change();

	var comp = jcnt.find("table:eq(0) > tbody > tr:eq(1) > td:eq(1) > lct-cell > label");
	equal(comp.html(), "description", "comp 20");

	var comp = jcnt.find("table:eq(0) > tbody > tr:eq(1) > td:eq(1) > lct-cell > lct-ctrl > textarea");
	equal(comp.text(), "", "comp desc");
	comp.focus();
	comp.text("JJ\nKKKK");

	var btn1 = jcnt.parent().find("div > div > button:eq(0)");
	equal(btn1.text(), 'Ok', 'btn 1');
	var btn2 = jcnt.parent().find("div > div > button:eq(1)");
	equal(btn2.text(), 'Annuler', 'btn 2');

	equal(this.mObsFactory.CallList.size(), 0, "Call A Nb :" + this.mObsFactory.CallList.toString());

	var content_base64 = btoa(content_file);
	var current_factory = this.mObsFactory;
	setTimeout(function() {
		start();

		btn1.click();
		ok(!gui.isExist(), "GUI exist");
		equal(current_factory.CallList.size(), 1, "Call B Nb :" + current_factory.CallList.toString());
		var expected_cmd = "lucterios.documents->documentAddModify(filename_FILENAME='undefined',description='JJ{[br/]}KKKK',SAVE='YES',)";
		equal(current_factory.CallList.get(0), expected_cmd, "Call #1");
	}, 600);
});

test("Custom_Download", function() {
	var json_receive = {
		"meta" : {
			"action" : "documentShow",
			"title" : "Afficher le document",
			"observer" : "core.custom",
			"extension" : "lucterios.documents"
		},
		"actions" : [ {
			"text" : "Modifier",
			"params" : null,
			"icon" : "/static/lucterios.CORE/images/edit.png",
			"modal" : "1",
			"unique" : "1",
			"id" : "lucterios.documents/documentAddModify",
			"action" : "documentAddModify",
			"close" : "1",
			"extension" : "lucterios.documents"
		}, {
			"text" : "Fermer",
			"icon" : "/static/lucterios.CORE/images/close.png",
			"modal" : "1",
			"unique" : "1",
			"id" : "",
			"params" : null,
			"close" : "1"
		} ],
		"comp" : [ {
			"x" : 1,
			"description" : "nom",
			"needed" : false,
			"tab" : 0,
			"rowspan" : 1,
			"component" : "LABELFORM",
			"y" : 1,
			"name" : "name",
			"colspan" : 2,
			"formatstr" : "{0}{0}",
			"formatnum" : null
		}, {
			"tab" : 0,
			"maxsize" : 0,
			"needed" : false,
			"filename" : "CORE/download?filename=documents/document_1&sign=4ac745f17656cfc30c3586b87d50e50a",
			"component" : "DOWNLOAD",
			"description" : "",
			"javascript" : "",
			"is_mini" : false,
			"is_default" : false,
			"x" : 1,
			"compress" : false,
			"action" : {
				"text" : "Ajouter",
				"params" : null,
				"icon" : "/static/lucterios.CORE/images/add.png",
				"modal" : "1",
				"unique" : "1",
				"id" : "filename",
				"action" : "documentAddModify",
				"name" : "filename",
				"close" : "0",
				"extension" : "lucterios.documents"
			},
			"rowspan" : 1,
			"y" : 2,
			"name" : "filename",
			"colspan" : 4,
			"http_file" : true
		} ],
		"data" : {
			"filename" : "modelstatus.doc",
			"name" : "modelstatus.doc",
		},
		"context" : {
			"LOCK_IDENT" : "lucterios.documents.models-Document-1",
			"document" : "1"
		},
		"close" : {
			"text" : "unlock",
			"params" : null,
			"modal" : "1",
			"unique" : "1",
			"id" : "CORE/unlock",
			"action" : "unlock",
			"close" : "1",
			"extension" : "CORE"
		}
	};
	var content_file = 'This file is part of Diacamma, a software developped by "Le Sanglier du Libre" (http://www.sd-libre.fr)\n'
			+ 'Thanks to have payed a retribution for using this module.\n' + '\n'
			+ 'Diacamma is free software; you can redistribute it and/or modify\n'
			+ 'it under the terms of the GNU General Public License as published by\n'
			+ 'the Free Software Foundation; either version 2 of the License, or\n' + '(at your option) any later version.\n' + '\n'
			+ 'Diacamma is distributed in the hope that it will be useful,\n' + 'but WITHOUT ANY WARRANTY; without even the implied warranty of\n'
			+ 'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n' + 'GNU General Public License for more details.\n' + '\n'
			+ 'You should have received a copy of the GNU General Public License\n' + 'along with Lucterios; if not, write to the Free Software\n'
			+ 'Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA';

	Singleton().Transport().JSONReceive = content_file;
	Singleton().mFileManager.saveBlob = $.proxy(this.saveBlob, this);
	equal(this.mFileContent, null, "Empty file");

	var obs = new ObserverCustom();
	obs.setSource("lucterios.documents", "documentShow");
	obs.setContent(json_receive);
	obs.show("Afficher le document", FORM_MODAL);

	var gui = obs.getGUI();
	ok(gui != null, "getGUI");
	ok(gui.isExist(), "GUI exist");
	var jcnt = gui.getHtmlDom();

	var comp_lbl = jcnt.find("table:eq(0) > tbody > tr:eq(1) > td:eq(1) > lct-cell > label");
	equal(comp_lbl.html(), 'modelstatus.doc', "comp filename");
	var comp_download = jcnt.find("table:eq(0) > tbody > tr:eq(1) > td:eq(1) > lct-cell > button");
	equal(comp_download.text(), 'Enregistrer sous...', "comp download");

	var btn1 = jcnt.parent().find("div:eq(2) > div:eq(0) > button:eq(0)");
	equal(btn1.text(), 'Modifier', 'btn 1');
	var btn2 = jcnt.parent().find("div:eq(2) > div:eq(0) > button:eq(1)");
	equal(btn2.text(), 'Fermer', 'btn 2');

	equal(this.mObsFactory.CallList.size(), 0, "Call A Nb :" + this.mObsFactory.CallList.toString());

	comp_download.click();
	equal(this.mFileName, "modelstatus.doc");
	ok(this.mFileContent != null, "File write");
	equal(this.mFileContent.size, content_file.length);
	equal(Singleton().Transport().XmlParam['URL'], 'CORE/download?filename=documents/document_1&sign=4ac745f17656cfc30c3586b87d50e50a');

	equal(this.mObsFactory.CallList.size(), 0, "Call B Nb :" + this.mObsFactory.CallList.toString());

	btn2.click();

});

test("Custom_Grid", function() {
	var json_receive = {
		"meta" : {
			"action" : "postalCodeList",
			"title" : "Code postal",
			"observer" : "core.custom",
			"extension" : "lucterios.contacts"
		},
		"actions" : [ {
			"text" : "Fermer",
			"icon" : "/static/lucterios.CORE/images/close.png",
			"modal" : "1",
			"unique" : "1",
			"id" : "",
			"params" : null,
			"close" : "1"
		} ],
		"comp" : [
				{
					"x" : 0,
					"description" : "",
					"needed" : false,
					"tab" : 0,
					"rowspan" : 1,
					"component" : "IMAGE",
					"y" : 0,
					"name" : "img",
					"colspan" : 1,
					"type" : ""
				},
				{
					"x" : 1,
					"description" : "",
					"needed" : false,
					"tab" : 0,
					"rowspan" : 1,
					"component" : "LABELFORM",
					"y" : 0,
					"name" : "filtre",
					"colspan" : 1,
					"formatstr" : "{0}",
					"formatnum" : null
				},
				{
					"tab" : 0,
					"needed" : false,
					"component" : "EDIT",
					"description" : "",
					"javascript" : "",
					"is_mini" : false,
					"size" : -1,
					"is_default" : false,
					"x" : 1,
					"reg_expr" : "",
					"action" : {
						"text" : "Code postal",
						"params" : null,
						"icon" : "/static/lucterios.contacts/images/postalCode.png",
						"modal" : "2",
						"unique" : "1",
						"id" : "filter_postal_code",
						"action" : "postalCodeList",
						"name" : "filter_postal_code",
						"close" : "0",
						"extension" : "lucterios.contacts"
					},
					"rowspan" : 1,
					"y" : 1,
					"name" : "filter_postal_code",
					"colspan" : 1
				},
				{
					"HMin" : 500,
					"tab" : 0,
					"needed" : false,
					"headers" : [ [ "postal_code", "code postal", "N0", 1, "{0}" ], [ "city", "ville", null, 1, "{0}" ],
							[ "country", "pays", null, 1, "{[b]}{0}{[/b]}" ] ],
					"VMin" : 200,
					"component" : "GRID",
					"description" : "",
					"page_max" : 1,
					"x" : 0,
					"order" : null,
					"actions" : [ {
						"text" : "Ajouter",
						"params" : null,
						"icon" : "/static/lucterios.CORE/images/add.png",
						"modal" : "1",
						"unique" : "0",
						"id" : "lucterios.contacts/postalCodeAdd",
						"action" : "postalCodeAdd",
						"close" : "0",
						"extension" : "lucterios.contacts"
					} ],
					"rowspan" : 1,
					"y" : 2,
					"name" : "postalCode",
					"colspan" : 2,
					"page_num" : 0
				}, {
					"x" : 0,
					"description" : "",
					"needed" : false,
					"tab" : 0,
					"rowspan" : 1,
					"component" : "LABELFORM",
					"y" : 3,
					"name" : "nb_postalCode",
					"colspan" : 2
				} ],
		"data" : {
			"nb_postalCode" : "Nombre total de codes postaux: 5",
			"img" : "/static/lucterios.contacts/images/postalCode.png",
			"filter_postal_code" : "3842",
			"postalCode" : [ {
				"city" : "DOMENE",
				"country" : "France",
				"postal_code" : 38420,
				"id" : 13052
			}, {
				"city" : "LE VERSOUD",
				"country" : "France",
				"postal_code" : 38420,
				"id" : 19686
			}, {
				"city" : "MURIANETTE",
				"country" : "France",
				"postal_code" : 38420,
				"id" : 41059
			}, {
				"city" : "REVEL",
				"country" : "France",
				"postal_code" : 38420,
				"id" : 26703
			}, {
				"city" : "ST JEAN LE VIEUX",
				"country" : "France",
				"postal_code" : 38420,
				"id" : 30019
			} ],
			"filtre" : "{[b]}Filtrer par code postal{[/b]}"
		},
		"context" : {
			"filter_postal_code" : "3842"
		},
		"close" : null
	};

	var obs = new ObserverCustom();
	obs.setSource("lucterios.contacts", "postalCodeList");
	obs.setContent(json_receive);
	obs.show("Code postal", FORM_MODAL);

	var gui = obs.getGUI();
	ok(gui != null, "getGUI");
	ok(gui.isExist(), "GUI exist");
	var jcnt = gui.getHtmlDom();

	var table_comp = jcnt.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0) > lct-cell");
	var table_header = table_comp.find("div.gridContent > table > thead > tr:eq(0)");
	var table_content = table_comp.find("div.gridContent > table > tbody");
	var table_buttons = table_comp.find("div.gridActions");

	var comp = table_header.find("th:eq(0)");
	equal(comp.text().trim(), "code postal", "head 1");
	var comp = table_header.find("th:eq(1)");
	equal(comp.text().trim(), "ville", "head 2");
	var comp = table_header.find("th:eq(2)");
	equal(comp.text().trim(), "pays", "head 3");

	var cell1 = table_content.find("tr:eq(0) > td:eq(0)");
	equal(cell1.text(), "38 420", "cell 1");
	var cell2 = table_content.find("tr:eq(1) > td:eq(1)");
	equal(cell2.text(), "LE VERSOUD", "cell 2");
	var cell3 = table_content.find("tr:eq(2) > td:eq(2)");
	equal(cell3.html(), "<b>France</b>", "cell 3");

	var btn1 = table_buttons.find('button:eq(0)');
	equal(btn1.text(), 'Ajouter', 'btn 1');
	equal(btn1.prop("disabled"), true, 'btn 1 disabled');

	var row2 = table_content.find("tr:eq(1)");
	equal(row2.hasClass("selected"), false, 'row 2 no-select');
	row2.click();

	equal(row2.hasClass("selected"), true, 'row 2:' + row2.attr('class'));
	equal(btn1.prop("disabled"), false, 'btn 1 enabled');

	equal(this.mObsFactory.CallList.size(), 0, "Call A Nb :" + this.mObsFactory.CallList.toString());

	btn1.click();
	equal(this.mObsFactory.CallList.size(), 1, "Call B Nb :" + this.mObsFactory.CallList.toString());
	equal(this.mObsFactory.CallList.get(0), "lucterios.contacts->postalCodeAdd(filter_postal_code='3842',postalCode='19686',)", "Call #0");

	gui.close();
	ok(!gui.isExist(), "GUI exist");

});

test("test_formating_general", function() {
	Singleton().mSelectLang = 'fr';

	equal(format_to_string(null, null, null), "---", "check null");
	equal(format_to_string("abc", null, null), "abc", "check string simple");
	equal(format_to_string("abc", null, "{0}"), "abc", "check string simple +");
	equal(format_to_string([ "abc", "uvw", "xyz" ], null, null), "abc{[br/]}uvw{[br/]}xyz", "check string multiple");
	equal(format_to_string("abc", null, "{[i]}{[b]}{0}{[/b]}{[/i]}"), "{[i]}{[b]}abc{[/b]}{[/i]}", "check string formated");
	equal(format_to_string([ "abc", "uvw", "xyz" ], null, "{0} : {1} --> {2}"), "abc : uvw --> xyz", "check string splited");
	equal(format_to_string([ 65.4, 456.04, 894730.124 ], "N2", "{0} : {1} --> {2}"), "65,40 : 456,04 --> 894 730,12", "check float splited");
	equal(format_to_string({
		"value" : "abc",
		"format" : "{[b]}{0}{[/b]}"
	}, null, "{[i]}{0}{[/i]}"), "{[i]}{[b]}abc{[/b]}{[/i]}", "check string riched formated");

	equal(format_to_string(1234.56, null, "{[i]}{0}{[/i]};{[b]}{0}{[/b]}"), "{[i]}1234.56{[/i]}", "check num positive");
	equal(format_to_string(-1234.56, null, "{[i]}{0}{[/i]};{[b]}{0}{[/b]}"), "{[b]}1234.56{[/b]}", "check num negative");

	equal(format_to_string(0.000001, 'C2EUR', '{0};A'), "A", "currency mode 0 null");
	equal(format_to_string(-0.000001, 'C2EUR', '{0};A'), "A", "currency mode 0 null");
	equal(format_to_string(-0.000001, 'C2EUR', '{0};A;B'), "B", "currency mode 0 null");
	equal(format_to_string(0.000001, 'C2EUR', '{0};A;B'), "B", "currency mode 0 null");

	equal(format_to_string(0, {
		'0' : 'aaa',
		'1' : 'bbb',
		'2' : 'ccc'
	}, "{0}"), "aaa", "check select 0");
	equal(format_to_string(1, {
		'0' : 'aaa',
		'1' : 'bbb',
		'2' : 'ccc'
	}, "{0}"), "bbb", "check select 1");
	equal(format_to_string(2, {
		'0' : 'aaa',
		'1' : 'bbb',
		'2' : 'ccc'
	}, "{0}"), "ccc", "check select 2");
	equal(format_to_string(3, {
		'0' : 'aaa',
		'1' : 'bbb',
		'2' : 'ccc'
	}, "{0}"), "3", "check select 3");
});

test("test_formating_fr", function() {
	Singleton().mSelectLang = 'fr';

	equal(format_to_string(1234.56, "N3", "{[i]}{0}{[/i]};{[b]}{0}{[/b]}"), "{[i]}1 234,560{[/i]}", "check num positive formated");
	equal(format_to_string(-1234.56, "N3", "{[i]}{0}{[/i]};{[b]}{0}{[/b]}"), "{[b]}1 234,560{[/b]}", "check num negative formated");
	equal(format_to_string(1234.56, "N0", "{0}"), "1 235", "check int no-formated");

	equal(format_to_string(1234.56, "N3", "{0}"), "1 234,560", "check num positive no-formated");
	equal(format_to_string(-1234.56, "N3", "{0}"), "-1 234,560", "check num negative no-formated");
	equal(format_to_string(1234.56, "C2EUR", "{0}"), "1 234,56 €", "check currency positive no-formated");
    equal(format_to_string(-1234.56, "C2EUR", "{0}"), "-1 234,56 €", "check currency negative no-formated");

	equal(format_to_string(1234.56, 'C2EUR', '{0};'), "1 234,56 €", "currency mode 0 +");
	equal(format_to_string(1234.56, 'C2EUR', 'Crédit {0};Débit {0}'), "Crédit 1 234,56 €", "currency mode 1 +");
	equal(format_to_string(1234.56, 'C2EUR', '{[font color="green"]}Crédit {0}{[/font]};{[font color="blue"]}Débit {0}{[/font]}'),
			"{[font color=\"green\"]}Crédit 1 234,56 €{[/font]}", "currency mode 2 +");
	equal(format_to_string(1234.56, 'N2', '{0}'), "1 234,56", "currency mode 3 +");
	equal(format_to_string(1234.56, 'C2EUR', '{0};{0}'), "1 234,56 €", "currency mode 4 +");
	equal(format_to_string(1234.56, 'C2EUR', '{0}'), "1 234,56 €", "currency mode 5 +");
	equal(format_to_string(1234.56, 'C2EUR', '{[font color="green"]}{0}{[/font]};{[font color="blue"]}{0}{[/font]}'),
			"{[font color=\"green\"]}1 234,56 €{[/font]}", "currency mode 6 +");

	equal(format_to_string(-1234.56, 'C2EUR', '{0};'), "", "currency mode 0 -");
	equal(format_to_string(-1234.56, 'C2EUR', 'Crédit {0};Débit {0}'), "Débit 1 234,56 €", "currency mode 1 -");
	equal(format_to_string(-1234.56, 'C2EUR', '{[font color="green"]}Crédit {0}{[/font]};{[font color="blue"]}Débit {0}{[/font]}'),
			"{[font color=\"blue\"]}Débit 1 234,56 €{[/font]}", "currency mode 2 -");
	equal(format_to_string(-1234.56, 'N2', '{0}'), "-1 234,56", "currency mode 3 -");
	equal(format_to_string(-1234.56, 'C2EUR', '{0};{0}'), "1 234,56 €", "currency mode 4 -");
	equal(format_to_string(-1234.56, 'C2EUR', '{0}'), "-1 234,56 €", "currency mode 5 -");
	equal(format_to_string(-1234.56, 'C2EUR', '{[font color="green"]}{0}{[/font]};{[font color="blue"]}{0}{[/font]}'),
			"{[font color=\"blue\"]}1 234,56 €{[/font]}", "currency mode 6 -");

	equal(format_to_string("2017-04-23", "D", "{0}"), "23 avril 2017", "check date");
	equal(format_to_string("12:54:25.014", "T", "{0}"), "12:54", "check time");
	equal(format_to_string("2017-04-23T12:54:25.014", "H", "{0}"), "dimanche 23 avril 2017 à 12:54", "check date time");

	equal(format_to_string(true, "B", "{0}"), "Oui", "check bool true");
	equal(format_to_string(false, "B", "{0}"), "Non", "check bool false");
});

test("test_formating_en", function() {
	Singleton().mSelectLang = 'en';

	equal(format_to_string(1234.56, "N3", "{[i]}{0}{[/i]};{[b]}{0}{[/b]}"), "{[i]}1,234.560{[/i]}", "check num positive formated");
	equal(format_to_string(-1234.56, "N3", "{[i]}{0}{[/i]};{[b]}{0}{[/b]}"), "{[b]}1,234.560{[/b]}", "check num negative formated");
	equal(format_to_string(1234.56, "N0", "{0}"), "1,235", "check int no-formated");

	equal(format_to_string(1234.56, "N3", "{0}"), "1,234.560", "check num positive no-formated");
	equal(format_to_string(-1234.56, "N3", "{0}"), "-1,234.560", "check num negative no-formated");
	equal(format_to_string(1234.56, "C2USD", "{0}"), "$1,234.56", "check currency positive no-formated");
    equal(format_to_string(-1234.56, "C2USD", "{0}"), "-$1,234.56", "check currency negative no-formated");

	equal(format_to_string("2017-04-23", "D", "{0}"), "April 23, 2017", "check date");
	equal(format_to_string("12:54:25.014", "T", "{0}"), "12:54 PM", "check time");
	equal(format_to_string("2017-04-23T12:54:25.014", "H", "{0}"), "Sunday, April 23, 2017, 12:54 PM", "check date time");

	equal(format_to_string(true, "B", "{0}"), "Yes", "check bool true");
	equal(format_to_string(false, "B", "{0}"), "No", "check bool false");
});
