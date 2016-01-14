module('TransportRest', {
	mFileContent : null,

	setup : function() {
		this.transport = new HttpTransportImpl();
		this.transport.close();
		$.removeCookie("sessionid");
	},
	teardown : function() {
		this.transport.close();
		this.transport = null;
		$.removeCookie("sessionid");
	},

	saveFile : function(aContent, aFileName) {
		this.mFileContent = atob(aContent);
		this.mFileName = aFileName;
	},

	convertXML : function(data) {
		data = data.replace(/>\s*/g, '>'); // Replace "> " with ">"
		data = data.replace(/\s*</g, '<'); // Replace "< " with "<"
		var parser = new DOMParser();
		var xmlDoc = parser.parseFromString(data, "text/xml");
		return (new XMLSerializer()).serializeToString(xmlDoc);
	},

});

test("Connection", function() {
	equal(this.transport.getServerUrl(), "http://127.0.0.1:8000/",
			"Server connect");
	equal(this.transport.getSession(), "", "session init");

	this.transport.setSession("ABCDEF12345");
	equal(this.transport.getSession(), "ABCDEF12345", "session final");
});

test("Static", function() {
	equal(this.transport.getSession(), "", "session init");
	this.transport.setSession("ABCDEF12345");
	equal(this.transport.getSession(), "ABCDEF12345", "session affected");

	var new_http_transport = new HttpTransportImpl();
	equal(new_http_transport.getSession(), "ABCDEF12345", "other session");
});

test(
		"Actions",
		function() {
			var xml_retour;
			post_log('cookie before:' + document.cookie);
			xml_retour = this.transport.transfertFileFromServerString(
					'CORE/menu', new HashMap());
			equal(
					this.convertXML(xml_retour),
					this
							.convertXML("<?xml version='1.0' encoding='utf-8'?><REPONSES><REPONSE observer='core.auth' source_extension='CORE' source_action='menu'>NEEDAUTH<TITLE>info</TITLE></REPONSE></REPONSES>"),
					"1er reponse");

			var params = new HashMap();
			params.put('username', 'admin');
			params.put('password', 'admin');
			xml_retour = this.transport.transfertFileFromServerString(
					'CORE/authentification', params);
			ok(140 <= xml_retour.length, "2eme reponse size");
			equal(
					this.convertXML(xml_retour).substring(0, 138),
					this
							.convertXML(
									"<?xml version='1.0' encoding='utf-8'?><REPONSES><REPONSE observer='core.auth' source_extension='CORE' source_action='authentification'>OK</REPONSE></REPONSES>")
							.substring(0, 138), "2eme reponse");

			var pos_in = xml_retour.indexOf('<PARAM name="ses">');
			ok(pos_in > 1, "Pas de session:" + xml_retour);
			var pos_out = xml_retour.indexOf("</PARAM>", pos_in);
			var session = xml_retour.substring(pos_in + 18, pos_out);
			this.transport.setSession(session);

			xml_retour = this.transport.transfertFileFromServerString(
					'CORE/menu', new HashMap());
			ok(128 <= xml_retour.length, "3eme reponse size");
			equal(
					this.convertXML(xml_retour).substring(0, 124),
					this
							.convertXML(
									"<?xml version='1.0' encoding='utf-8'?><REPONSES><REPONSE observer='core.menu' source_extension='CORE' source_action='menu'><MENU/></REPONSE></REPONSES>")
							.substring(0, 124), "3eme reponse:"
							+ xml_retour.substring(0, 256));
			post_log('cookie after:' + document.cookie);
		});

asyncTest("File", function() {
	if (typeof (Blob) === typeof (Function)) {
		equal(this.mFileContent, null, 'init');
		Singleton().mFileManager.saveFile = $.proxy(this.saveFile, this);
		this.transport.getFileContent('static/lucterios.CORE/images/add.png', function(blob) {
			Singleton().mFileManager.saveBlob(blob, 'add.png');
		});
		var transp_test = this;

		setTimeout(function() {
			start();
			equal(transp_test.mFileContent.length, 1415, 'size');
			equal(transp_test.mFileContent.substr(1, 3), "PNG")
		}, 300);
	} else {
		start();
		ok(true, "NO BLOB MANAGE");
	}
});
