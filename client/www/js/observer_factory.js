/*global Class,HashMap,unusedVariables,LucteriosException,GRAVE,IMPORTANT,POST_VARIABLE,post_log*/

var ObserverFactoryAbstract = Class.extend({
	m_Parameters : "",
	mTransport : null,
	mObserverList : new HashMap(),

	init : function() {
		return undefined;
	},

	setHttpTransport : function(aHttpTransport) {
		this.mTransport = aHttpTransport;
	},

	clearObserverList : function() {
		this.mObserverList = new HashMap();
	},

	AddObserver : function(aObsName, aObserverClass) {
		this.mObserverList.put(aObsName, aObserverClass);
	},

	factoryObserver : function(aObserverName) {
		var observer_class = this.mObserverList.get(aObserverName);
		return new observer_class();
	},

	transfertFromServer : function(aExtension, aAction, aParam, aMethod) {
		unusedVariables(aExtension, aAction, aParam, aMethod);
		return null;
	},

	callAction : function(aExtension, aAction, aParam, aMethod) {
		unusedVariables(aExtension, aAction, aParam, aMethod);
		return null;
	},

	setAuthentification : function(aLogin, aPassWord) {
		var res = false, param = new HashMap(), aut, xml_aut, session;
		if ((aLogin === null)) {
			param.put('ses', aPassWord);
			param.put('info', "1");
		} else {
			param.put('username', aLogin);
			param.put('password', aPassWord);
			this.mTransport.setLastLogin(aLogin);
		}
		aut = this.callAction('CORE', "authentification", param, null, "POST");
		if (aut.getObserverName() === "core.auth") {
			xml_aut = aut.getContent();
			if (xml_aut.context && xml_aut.context.ses) {
				session = xml_aut.context.ses;
				res = (session !== '');
				if (res) {
					this.mTransport.setSession(session);
				}
			}
		}
		aut.show("");
		return res;
	}
});

var ObserverFactoryImpl = ObserverFactoryAbstract.extend({

	callAction : function(aExtension, aAction, aParam, aObserver, aMethod) {
		var res_obs = null, json_rep = this.transfertFromServer(aExtension, aAction, aParam, aMethod), observer_name, source_extension, source_action;
		if (json_rep && json_rep.meta) {
			observer_name = json_rep.meta.observer;
			if (this.mObserverList.hasOwnProperty(observer_name)) {
				source_extension = json_rep.meta.extension;
				source_action = json_rep.meta.action;
				if (aObserver === null) {
					res_obs = this.factoryObserver(observer_name);
					res_obs.setSource(source_extension, source_action, aMethod);
				} else {
					res_obs = aObserver;
					if ((res_obs.getObserverName() !== observer_name) || (source_action === "") || (source_extension === "")) {
						if ((observer_name === "core.auth") || (observer_name === "core.exception")) {
							res_obs = this.factoryObserver(observer_name);
							res_obs.setSource(source_extension, source_action, aMethod);
						} else {
							throw new LucteriosException(GRAVE, "Erreur de parsing (refresh)" + aObserver.getObserverName() + " -> " + observer_name,
									this.m_Parameters, JSON.stringify(json_rep));
						}
					}
				}
				if (json_rep.meta.title) {
					res_obs.setCaption(json_rep.meta.title);
				} else {
					res_obs.setCaption("");
				}
				res_obs.setContent(json_rep);
			} else {
				throw new LucteriosException(IMPORTANT, "Observeur '" + observer_name + "' inconnu.", this.m_Parameters, JSON.stringify(json_rep));
			}
		} else {
			throw new LucteriosException(GRAVE, "Erreur inconnu", this.m_Parameters, json_rep.toString());
		}
		return res_obs;
	}
});

var ObserverFactoryRestImpl = ObserverFactoryImpl.extend({
	transfertFromServer : function(aExtension, aAction, aParam, aMethod) {
		var val, self = this, web_file = aExtension + "/" + aAction;
		this.m_Parameters = web_file + "?";
		aParam.keys().forEach(function(key) {
			val = aParam.get(key);
			if (typeof val === 'string') {
				if (self.m_Parameters !== '') {
					self.m_Parameters += '&';
				}
				self.m_Parameters += key + "=" + val;
			} else {
				if (val instanceof Blob) {
					if (self.m_Parameters !== '') {
						self.m_Parameters += '&';
					}
					self.m_Parameters += key + "=" + val.name;
				}
			}
		});
		post_log("Ask " + self.m_Parameters);
		return this.mTransport.transfertFileFromServerString(web_file, aParam, aMethod);
	}
});
