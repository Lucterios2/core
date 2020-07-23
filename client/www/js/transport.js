/*global $,Singleton,Class,get_serverurl,unusedVariables,post_log,LucteriosException,IMPORTANT,CRITIC,GRAVE */

var HttpTransportAbstract = Class.extend({
	mLastLogin : '',

	init : function() {
		return undefined;
	},

	setLastLogin : function(aLastLogin) {
		this.mLastLogin = aLastLogin;
	},

	getLastLogin : function() {
		return this.mLastLogin;
	},

	getServerUrl : function() {
		return get_serverurl();
	},

	getSession : function() {
		var session = this.getSessionEx();
		this.setSession(session);
		return session;
	},

	getSessionEx : function() {
		var session = $.cookie("lucterios_session");
		if (session === undefined) {
			session = "";
		}
		return session;
	},

	setSession : function(session) {
		if (session === '') {
			$.removeCookie("lucterios_session");
			$.removeCookie("sessionid");
		} else {
			$.cookie("lucterios_session", session, {
				expires : 1
			});
		}
	},

	transfertFileFromServerString : function(aWebFile, aParams, aMethod) {
		unusedVariables(aWebFile, aParams, aMethod);
		return "";
	},

	getIconUrl : function(icon) {
		if (/^data:image/.test(icon)) {
			return icon;
		}
		var icon_url = get_serverurl();
		if (icon[0] === '/') {
			icon_url += icon.substring(1);
		} else {
			icon_url += icon;
		}
		return icon_url;
	},

	close : function() {
		return this.setSession("");
	},

	getFileContent : function(aUrl) {
		unusedVariables(aUrl);
	}

});

var HttpTransportImpl = HttpTransportAbstract.extend({

	transfertFileFromServerString : function(aWebFile, aParams, aMethod) {
		var reponsetext = "", formdata = new FormData(), error_num = -1, code_error, url_params = "", parts;
		if (aMethod === undefined) {
			aMethod = "GET";
		}
		if (aParams !== null) {
			if (aMethod === 'GET') {
				parts = [];
				aParams.keys().forEach(function(key) {
					parts.push("{0}={1}".format(encodeURIComponent(key), encodeURIComponent(aParams[key])));
				});
				url_params = "?" + parts.join('&');
			} else {
				aParams.keys().forEach(function(key) {
					formdata.append(key, aParams.get(key));
				});
			}
		}
		formdata.append('FORMAT', 'JSON');

		$.ajax({
			url : this.getServerUrl() + aWebFile + url_params,
			type : aMethod,
			data : formdata,
			dataType : "json",
			processData : false,
			contentType : false,
			async : false,
			success : function(data) {
				reponsetext = data;
			},
			error : function(xhr, textStatus, errorThrown) {
				post_log('HTTP ERROR:' + xhr.statusText + "/" + textStatus + "/" + errorThrown);
				error_num = xhr.readyState;
				code_error = xhr.status;
				reponsetext = errorThrown;
			}
		});
		if (error_num !== -1) {
			if (error_num === 0) {
				throw new LucteriosException(IMPORTANT, Singleton().getTranslate('Lost connection!'), aWebFile, reponsetext);
			} else {
				if (code_error === 404) {
					throw new LucteriosException(GRAVE, Singleton().getTranslate('Command unknown!'), aWebFile, reponsetext);
				} else {
					throw new LucteriosException(CRITIC, 'Http error ' + code_error, aWebFile, reponsetext);
				}
			}
		}
		return reponsetext;
	},

	close : function() {
		if (this.getSessionEx() !== '') {
			var act = Singleton().CreateAction();
			if (act !== null) {
				act.initializeEx(null, Singleton().Factory(), '', 'CORE', 'exitConnection');
				act.actionPerformed();
			}
		}
		return this._super();
	},

	getFileContent : function(aUrl, callback) {
		var xhr = new XMLHttpRequest();
		xhr.open('POST', this.getServerUrl() + aUrl, true);
		xhr.responseType = 'blob';
		xhr.onload = function(e) {
			unusedVariables(e);
			if (this.status === 200) {
				callback(this.response);
			}
		};
		xhr.send();
	}

});

var HttpTransportLocal = HttpTransportAbstract.extend({

	getIconUrl : function(icon) {
		var icon_list = icon.split('/');
		return "images/" + icon_list[icon_list.length - 1];
	}

});
