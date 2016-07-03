/*global $,singleton,Class,get_serverurl,unusedVariables,post_log,LucteriosException,IMPORTANT,CRITIC, FormData*/
'use strict';

var ENCODE = "utf-8";
var MANAGER_FILE = "coreIndex.php";
var AUTH_PARAM = "<PARAM name='ses' type='str'>";
var MANAGER_FILE = "coreIndex.php";
var POST_VARIABLE = "XMLinput";
var NOENCODE = "nourlencode";

var HttpTransportAbstract = Class
		.extend({
			mLastLogin : '',

			init : function () {
				return undefined;
			},

			setLastLogin : function (aLastLogin) {
				this.mLastLogin = aLastLogin;
			},

			getLastLogin : function () {
				return this.mLastLogin;
			},

			getServerUrl : function () {
				return get_serverurl();
			},

			getSession : function () {
				var session = this.getSessionEx();
				this.setSession(session);
				return session;
			},

			getSessionEx : function () {
				var session = $.cookie("lucterios_session");
				if (session === undefined) {
					session = "";
				}
				return session;
			},

			setSession : function (session) {
				if (session === '') {
					$.removeCookie("lucterios_session");
					$.cookie('sessionid', '', {
						path : '/'
					});
					$.cookie('sessionid', '', {
						path : '/web/'
					});
				} else {
					$.cookie("lucterios_session", session, {
						expires : 0.025
					});
				}
			},

			transfertFileFromServerString : function (aWebFile, aParams) {
				unusedVariables(aWebFile, aParams);
				return "";
			},

			getIconUrl : function (icon) {
				var icon_url = get_serverurl();
				if (icon[0] === '/') {
					icon_url += icon.substring(1);
				} else {
					icon_url += icon;
				}
				return icon_url;
			},

			transfertXMLFromServer : function (aParams) {
				var AUTH_REQUETE = "<REQUETE extension='CORE' action='authentification'>", xml_param = "<?xml version='1.0' encoding='"
                    + ENCODE + "'?>", post_xml, data, reponse;
				xml_param = xml_param + "<REQUETES>\n";
				post_xml = '';
				if (aParams.hasOwnProperty(POST_VARIABLE)) {
					post_xml = aParams.get(POST_VARIABLE);
				}
				if ((this.getSessionEx() !== "")
						&& (post_xml.indexOf(AUTH_REQUETE) === -1)) {
					xml_param = xml_param + AUTH_REQUETE;
					xml_param = xml_param + AUTH_PARAM + this.getSessionEx()
							+ "</PARAM>";
					xml_param = xml_param + "</REQUETE>";
				}
				xml_param = xml_param + post_xml + "</REQUETES>";
				post_log("Ask " + xml_param);
				aParams.put(POST_VARIABLE, xml_param);
				aParams.put(NOENCODE, "1");
				data = this
						.transfertFileFromServerString(MANAGER_FILE, aParams);
				reponse = "<?xml version='1.0' encoding='ISO-8859-1'?>"
						+ data.replace(/\n/g, "");
				return reponse;
			},

			close : function () {
				return this.setSession("");
			},

			getFileContent : function (aUrl) {
				unusedVariables(aUrl);
			}

		});

var HttpTransportImpl = HttpTransportAbstract.extend({

	transfertFileFromServerString : function (aWebFile, aParams) {
		var reponsetext = "", formdata = new FormData(), error_num = -1;
		if (aParams !== null) {
			aParams.keys().forEach(function (key) {
				formdata.append(key, aParams.get(key));
			});
		}

		$.ajax({
			url : this.getServerUrl() + aWebFile,
			type : "POST",
			data : formdata,
			dataType : "text",
			processData : false,
			contentType : false,
			async : false,
			success : function (data) {
				reponsetext = data;
			},
			error : function (xhr, textStatus, errorThrown) {
				post_log('HTTP ERROR:' + xhr.statusText + "/" + textStatus
						+ "/" + errorThrown);
				error_num = xhr.readyState;
				reponsetext = errorThrown;
			}
		});
		if (error_num !== -1) {
			if (error_num === 0) {
				throw new LucteriosException(IMPORTANT, singleton()
						.getTranslate('Lost connection!'), aWebFile,
						reponsetext);
			} else {
				throw new LucteriosException(CRITIC, 'Http error', aWebFile,
						reponsetext);
			}
		}
		return reponsetext;
	},

	close : function () {
		if (this.getSessionEx() !== '') {
			var act = singleton().CreateAction();
			if (act !== null) {
				act.initializeEx(null, singleton().Factory(), '', 'CORE',
						'exitConnection');
				act.actionPerformed();
			}
		}
		return this._super();
	},

	getFileContent : function (aUrl, callback) {
		var xhr = new XMLHttpRequest();
		xhr.open('POST', this.getServerUrl() + aUrl, true);
		xhr.responseType = 'blob';
		xhr.onload = function (e) {
			unusedVariables(e);
			if (this.status === 200) {
				callback(this.response);
			}
		};
		xhr.send();
	}

});
