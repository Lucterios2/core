/*global $,Class,navigator,ObserverAbstract,G_Version,ActionInt,Singleton,HashMap,compBasic,GUIManage,createTable,unusedVariables,get_serverurl,run_CleanCallBack */

var ApplicationDescription = Class.extend({

	mTitle : '',
	mApplisVersion : '',
	mServerVersion : '',
	mCopyRigth : '',
	mLogoIconName : '',
	mBackground : '',
	mLogin : '',
	mInfoServer : '',
	mSupportEmail : '',
	mSupportHTML : '',
	mSubTitle : '',
	mRealName : '',
	mInstanceName : '',
	mMode : 0,
	mLanguage : '',

	init : function(aTitle, aCopyRigth, aAppliVersion, aServerVersion) {
		this.mTitle = aTitle;
		this.mApplisVersion = aAppliVersion;
		this.mServerVersion = aServerVersion;
		this.mCopyRigth = aCopyRigth;
	},

	setLogoIconName : function(aLogoIconName) {
		this.mLogoIconName = aLogoIconName;
	},

	setBackground : function(aBackground) {
		this.mBackground = aBackground;
	},

	getTitle : function() {
		return this.mTitle;
	},

	getConnectUser : function() {
		var res = this.mRealName;
		if (this.mLogin !== '') {
			res += " ({0}@{1})".format(this.mLogin, this.mInstanceName);
		} else {
			res += " @{0}".format(this.mInstanceName);
		}
		return res;
	},

	getLogoIconName : function() {
		return this.mLogoIconName;
	},

	getApplisVersion : function() {
		return this.mApplisVersion;
	},

	getServerVersion : function() {
		return this.mServerVersion;
	},

	getCopyRigth : function() {
		return this.mCopyRigth;
	},

	getInfoServer : function() {
		return this.mInfoServer;
	},

	getSupportEmail : function() {
		return this.mSupportEmail;
	},

	getSupportHTML : function() {
		return this.mSupportHTML;
	},

	getLogin : function() {
		return this.mLogin;
	},

	getSubTitle : function() {
		return this.mSubTitle;
	},

	getRealName : function() {
		return this.mRealName;
	},

	getMode : function() {
		return this.mMode;
	},

	setLogin : function(aLogin) {
		this.mLogin = aLogin;
	},

	setInfoServer : function(aInfoServer) {
		this.mInfoServer = aInfoServer;
	},

	setSupportEmail : function(aSupportEmail) {
		this.mSupportEmail = aSupportEmail;
	},

	setSupportHTML : function(aSupportHTML) {
		this.mSupportHTML = aSupportHTML;
	},

	setSubTitle : function(aSubTitle) {
		this.mSubTitle = aSubTitle;
	},

	setRealName : function(aRealName) {
		this.mRealName = aRealName;
	},

	setMode : function(aMode) {
		this.mMode = aMode;
	},

	setInstanceName : function(aInstanceName) {
		this.mInstanceName = aInstanceName;
	},

	getLanguage : function() {
		return this.mLanguage;
	},

	setLanguage : function(language) {
		this.mLanguage = language;
	},

	fillEmailSupport : function(aTitle, aComplement) {
		var email = this.mSupportEmail, url = "mailto:" + email;
		url += "?subject=" + aTitle;
		url += "&body=" + this.getText(aComplement).replace("+", " ");
		return url;
	},

	getHTML : function(aComplement) {
		var resValue = "";
		if ((aComplement !== null) && (aComplement.length > 0)) {
			resValue += aComplement + "<br>";
		}
		resValue += "<hr><center><h1>" + this.mTitle + "</h1></center>" + "<table width='100%'>" + "<tr><td><center>"
				+ Singleton().getTranslate("Version") + "</center></td><td><center>" + this.mApplisVersion + "</center></td></tr>"
				+ "<tr><td><center>" + Singleton().getTranslate("Server") + "</center></td><td><center>" + this.mServerVersion
				+ "</center></td></tr>" + "<tr><td><center>" + Singleton().getTranslate("AJAX Client") + "</center></td><td><center>" + G_Version
				+ "</center></td></tr>" + "<tr><td><center>" + Singleton().getTranslate("Browser") + "</center></td><td><center><font size='-1'>"
				+ navigator.userAgent.replace(') ', ')<br>') + "</font></center></td></tr>" + "<tr><td><center>"
				+ Singleton().getTranslate("Connection") + "</center></td><td><center><font size='-1'>" + this.getConnectUser() + '<br>'
				+ get_serverurl() + "</font></center></td></tr>" + "<tr><td colspan='2'><center><font size='-1'><i>" + this.mCopyRigth
				+ "</i></font></center></td></tr>" + "</table><hr>";
		if ((this.mInfoServer !== null) && (this.mInfoServer.length > 0)) {
			resValue += this.mInfoServer.convertLuctoriosFormatToHtml() + "<br>";
		}
		return resValue;
	},

	getText : function(aComplement) {
		var text_html = this.getHTML(aComplement), pos1 = 1, pos2 = 1;
		while ((pos1 > 0) && (pos2 > 0)) {
			pos1 = text_html.indexOf("<style type=\"text/css\">");
			pos2 = text_html.indexOf("</style>");
			if ((pos1 > 0) && (pos2 > 0)) {
				text_html = text_html.substring(0, pos1) + text_html.substring(pos2 + 10);
			}
		}
		text_html = text_html.replace(
				/(<center>|<\/center>|<table width='100%'>|<\/table>|<tr><td>|<tr><td colspan='2'>|<font size='-1'>|<\/font>|<i>|<\/i>)/g, "");
		text_html = text_html.replace(/<h1>\s*/g, "#### ");
		text_html = text_html.replace(/[<br>|\\s|\n]*<\/h1>/g, " ####\n");
		text_html = text_html.replace("<b>", "[");
		text_html = text_html.replace("</b>", "]");
		text_html = text_html.replace("&#60;", "<");
		text_html = text_html.replace("&#61;", "=");
		text_html = text_html.replace("&#62;", ">");
		text_html = text_html.replace("&#95;", "_");
		text_html = text_html.replace("&#39;", "'");
		text_html = text_html.replace("&#32;", " ");
		text_html = text_html.replace("&#33;", "!");
		text_html = text_html.replace("&#91;", "[");
		text_html = text_html.replace("&#93;", "]");
		text_html = text_html.replace("&#47;", "/");
		text_html = text_html.replace(/(<\/td><\/tr>|<br>|<br\/>)/g, "\n");
		text_html = text_html.replace(/<\/td><td>/g, " : ");
		text_html = text_html.replace(/(<hr>|<hr\/>)/g, "__________________________________________\n");
		return encodeURIComponent(text_html);
	}
});

var ObserverAuthentification = ObserverAbstract.extend({
	refreshMenu : true,

	acts : null,

	mActions : null,

	getObserverName : function() {
		return "core.auth";
	},

	setContent : function(aDomXmlContent) {
		this._super(aDomXmlContent);
		this.acts = [];
		this.acts[0] = new ActionInt();
		this.acts[0].initializeEx(this, null, 'Ok');
		this.acts[0].mIcon = "static/lucterios.CORE/images/ok.png";
		this.acts[0].callback = $.proxy(function(aParams) {
			if (this.mGUI !== null) {
				var login = aParams.get('username'), pass = aParams.get('password');
				Singleton().Factory().setAuthentification(login, pass);
			}
		}, this);
		this.acts[1] = new ActionInt();
		this.acts[1].initializeEx(this, Singleton().Factory(), Singleton().getTranslate("Cancel"));
		this.acts[1].mIcon = "static/lucterios.CORE/images/cancel.png";
		this.acts[1].callback = function() {
			Singleton().setInfoDescription(null, false);
		};
		this.mActions = this.mDomXmlContent.getFirstTag("ACTIONS");
	},

	show : function(aTitle, aGUIType) {
		this._super(aTitle, aGUIType);
		var cdate = this.mDomXmlContent.getTextFromXmlNode().trim(), xml_connection, desc, xml_params, param_idx;
		if (cdate !== "OK") {
			Singleton().Transport().setSession("");
			run_CleanCallBack();
			this.show_logon(cdate);
			this.refreshMenu = true;
		} else {
			xml_connection = this.mDomXmlContent.getElementsByTagName("CONNECTION")[0];
			desc = new ApplicationDescription(xml_connection.getCDataOfFirstTag("TITLE"), xml_connection.getCDataOfFirstTag("COPYRIGHT"),
					xml_connection.getCDataOfFirstTag("VERSION"), xml_connection.getCDataOfFirstTag("SERVERVERSION"));
			desc.setLogoIconName(xml_connection.getCDataOfFirstTag("LOGONAME"));
			desc.setBackground(xml_connection.getCDataOfFirstTag("BACKGROUND"));
			desc.setSupportEmail(xml_connection.getCDataOfFirstTag("SUPPORT_EMAIL"));
			desc.setSupportHTML(xml_connection.getCDataOfFirstTag("SUPPORT_HTML"));
			desc.setInfoServer(xml_connection.getCDataOfFirstTag("INFO_SERVER"));
			desc.setSubTitle(xml_connection.getCDataOfFirstTag("SUBTITLE"));
			desc.setLogin(xml_connection.getCDataOfFirstTag("LOGIN"));
			desc.setRealName(xml_connection.getCDataOfFirstTag("REALNAME"));
			desc.setMode(xml_connection.getCDataOfFirstTag("MODE"));
			desc.setInstanceName(xml_connection.getCDataOfFirstTag("INSTANCE"));
			desc.setLanguage(xml_connection.getCDataOfFirstTag("LANGUAGE"));
			xml_params = this.mDomXmlContent.getElementsByTagName("PARAM");
			for (param_idx = 0; param_idx < xml_params.length; param_idx++) {
				if (xml_params[param_idx].getAttribute('name') === 'ses') {
					Singleton().Transport().setSession(xml_params[param_idx].getTextFromXmlNode());
				}
			}
			Singleton().setInfoDescription(desc, this.refreshMenu);
			this.refreshMenu = false;
		}
	},

	getParameters : function(aCheckNull) {
		unusedVariables(aCheckNull);
		var requete = new HashMap(), jcnt, login, pass;
		if (this.mGUI !== null) {
			jcnt = this.mGUI.getHtmlDom();
			login = jcnt.find("table:eq(0) > tbody > tr:eq(1) > td:eq(1) > input");
			requete.put('username', login.val());
			pass = jcnt.find("table:eq(0) > tbody > tr:eq(2) > td:eq(1) > input");
			requete.put('password', pass.val());
			$('#frm_' + this.mGUI.mId).submit();
		}
		return requete;
	},

	closeEx : function() {
		if (this.mGUI !== null) {
			this.mGUI.dispose();
		}
	},

	getRefreshMenu : function() {
		return this.refreshMenu;
	},

	show_logon : function(cdate) {
		var text = "", table = [], index, xml_actions, extra_acts = [], extra_table = [];
		if (Singleton().Transport().getLastLogin() !== '') {
			if ("BADAUTH" === cdate) {
				text = Singleton().getTranslate("Login or password wrong!", "Alias ou Mot de passe incorrect!");
			} else if ("NEEDAUTH" === cdate) {
				text = Singleton().getTranslate("Please, identify you");
			} else if ("BADSESS" === cdate) {
				text = Singleton().getTranslate("Expired session!");
			} else if ("BADFROMLOCATION" === cdate) {
				text = Singleton().getTranslate("Connection forbideen in this localisation!");
			} else if (cdate !== '') {
				text = "'" + cdate + "'";
			}
		}

		table[0] = [];
		table[0][0] = new compBasic('<label style="width:100%;text-align:center;color:red;">' + text + '</label>', 2);

		table[1] = [];
		table[1][0] = new compBasic('<span style="width:95%;margin:5px;"><b>' + Singleton().getTranslate("Login") + '</b></span>');
		table[1][1] = new compBasic('<input name="username" type="text" style="width:95%;margin:5px;"/>');

		table[2] = [];
		table[2][0] = new compBasic('<span style="width:95%;margin:5px;"><b>' + Singleton().getTranslate("Password") + '</b></span>');
		table[2][1] = new compBasic('<input name="password" type="password" style="width:95%;margin:5px;"/>');
		if (this.mActions !== null) {
			xml_actions = this.mActions.getElementsByTagName("ACTION");
			extra_table[0] = [];
			for (index = 0; index < xml_actions.length; index++) {
				extra_acts[index] = Singleton().CreateAction();
				extra_acts[index].initialize(this, Singleton().Factory(), xml_actions[index]);
				extra_table[0][index] = new compBasic('<center><button id="btn_{0}_{1}"><span style="font-size:10px;">{2}</span></button></center>'
						.format(this.getId(), index, extra_acts[index].getTitle()));
			}
			table[3] = [];
			table[3][0] = new compBasic(createTable(extra_table), 2);
		}
		this.mGUI = new GUIManage(this.getId(), Singleton().getTranslate("Logon"), this);
		this.mGUI.withForm = true;
		this.mGUI.addcontent(createTable(table), this.acts);
		this.mGUI.showGUI(true);
		for (index = 0; index < extra_acts.length; index++) {
			$('#btn_{0}_{1}'.format(this.getId(), index)).click($.proxy(extra_acts[index].actionPerformed, extra_acts[index]));
		}
		$('#frm_' + this.mGUI.mId).submit(function(event) {
			event.preventDefault();
		});

		$('#frm_' + this.mGUI.mId).find("[name='password'],[name='username']").bind("keydown", function(event) {
			var result, keycode = (event.keyCode || event.which || event.charCode);
			if (keycode === 13) {
				$("button.ui-button-text-only")[0].click();
				result=false;
			} else {
				result=true;
			}
			return result;
		});
	}

});
