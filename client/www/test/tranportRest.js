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
	equal(this.transport.getServerUrl(), "http://127.0.0.1:8000/", "Server connect");
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

test("Actions", function() {
	var json_retour;
	post_log('cookie before:' + document.cookie);
	json_retour = this.transport.transfertFileFromServerString('CORE/menu', new HashMap());
	equal(json_retour.connexion.INSTANCE, "test", "1er response connexion");
	delete json_retour.connexion;
	propEqual(json_retour, {
		data : "NEEDAUTH",
		close : null,
		context : {},
		meta : {
			action : "menu",
			observer : "core.auth",
			title : "info",
			extension : "CORE"
		}
	}, "1er reponse");

	var params = new HashMap();
	params.put('username', 'admin');
	params.put('password', 'admin');
	json_retour = this.transport.transfertFileFromServerString('CORE/authentification', params ,'POST');
	equal(Object.keys(json_retour).length, 5, "2eme reponse size");
	equal(json_retour.data, "OK", "2eme reponse - data");
	equal(json_retour.close, null, "2eme reponse - close");
	propEqual(json_retour.context, {
		password : "admin",
		username : "admin",
		ses : "admin"
	}, "2eme reponse - context");
	propEqual(json_retour.meta, {
		action : "authentification",
		observer : "core.auth",
		title : "info",
		extension : "CORE"
	}, "2eme reponse - meta");
	equal(Object.keys(json_retour.connexion).length, 19, "2eme reponse connexion size");
	this.transport.setSession(json_retour.context.session);

	json_retour = this.transport.transfertFileFromServerString('CORE/menu', new HashMap());
	equal(Object.keys(json_retour).length, 4, "3eme reponse size");
	equal(json_retour.close, null, "3eme reponse - close");
	propEqual(json_retour.context, {}, "3eme reponse - context");
	propEqual(json_retour.meta, {
		action : "menu",
		observer : "core.menu",
		title : "menu",
		extension : "CORE"
	}, "3eme reponse - meta");
	equal(json_retour.menus.length, 4, "3eme reponse menu size");
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
