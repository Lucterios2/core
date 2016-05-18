/*global Class,HashMap,unusedVariables,LucteriosException,GRAVE,IMPORTANT,POST_VARIABLE,post_log*/

var ObserverFactoryAbstract = Class
		.extend({
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

			factoryObserver : function(aObserverName, aParamTxt, aXmlText) {
				unusedVariables(aParamTxt, aXmlText);
				var observer_class = this.mObserverList.get(aObserverName);
				return new observer_class();
			},

			transfertFromServer : function(aExtension, aAction, aParam) {
				unusedVariables(aExtension, aAction, aParam);
				return null;
			},
			
			callAction : function(aExtension, aAction, aParam) {
				unusedVariables(aExtension, aAction, aParam);
				return null;
			},

			setAuthentification : function(aLogin, aPassWord) {
				var res = false, param = new HashMap(), aut, xml_aut, xml_params, session;
				if ((aLogin === null)) {
					param.put('ses', aPassWord);
					param.put('info', "1");
				} else {
					param.put('username', aLogin);
					param.put('password', aPassWord);
					this.mTransport.setLastLogin(aLogin);
				}
				aut = this.callAction('CORE', "authentification",
						param, null);
				if (aut.getObserverName() === "core.auth") {
					xml_aut = aut.getContent();
					xml_params = xml_aut.getElementsByTagName("PARAM");
					if (xml_params.length > 0) {
						session = xml_params[0].childNodes.length > 0 ? xml_params[0].childNodes[0].nodeValue
								: '';
						res = (session !== '');
						if (res) {
							this.mTransport.setSession(session);
						}
					}
					aut.show("");
				}
				return res;
			}
		});

var ObserverFactoryImpl = ObserverFactoryAbstract
		.extend({

			callAction : function(aExtension, aAction, aParam, aObserver) {
				var res_obs = null, xml_text = this.transfertFromServer(
						aExtension, aAction, aParam), reps = xml_text
						.parseXML(), rep = null, idx, observer_name, titles, source_extension, source_action, errorMsg;
				post_log("==>  reponse :" + xml_text);
				for (idx = 0; (reps !== null) && (rep === null)
						&& (idx < reps.childNodes.length); idx++) {
					if (reps.childNodes[idx].nodeName === 'REPONSE') {
						rep = reps.childNodes[idx];
					}
				}
				if (rep !== null) {
					observer_name = rep.getAttribute("observer");
					if (this.mObserverList.hasOwnProperty(observer_name)) {
						source_extension = rep.getAttribute("source_extension");
						source_action = rep.getAttribute("source_action");
						if (aObserver === null) {
							res_obs = this.factoryObserver(observer_name,
									this.m_XMLParameters, xml_text);
							res_obs.setSource(source_extension, source_action);
						} else {
							res_obs = aObserver;
							if ((res_obs.getObserverName() !== observer_name)
									|| (source_action === "")
									|| (source_extension === "")) {
								if ((observer_name === "core.auth")
										|| (observer_name === "core.exception")) {
									res_obs = this.factoryObserver(
											observer_name,
											this.m_XMLParameters, xml_text);
									res_obs.setSource(source_extension,
											source_action);
								} else {
									throw new LucteriosException(GRAVE,
											"Erreur de parsing xml (refresh)"
													+ aObserver
															.getObserverName()
													+ " -> " + observer_name,
											this.m_XMLParameters, xml_text);
								}
							}
						}
						titles = rep.getElementsByTagName("TITLE");
						if (titles.length > 0) {
							res_obs.setCaption(titles[0].getTextFromXmlNode());
						} else {
							res_obs.setCaption("");
						}
						res_obs.setContent(rep);
					} else {
						throw new LucteriosException(
								IMPORTANT,
								"Observeur '"
										+ observer_name
										+ "' inconnu{[newline]}Veuillez utiliser le client Java.",
								this.m_XMLParameters, xml_text);
					}
				} else {
					errorMsg = "**";
					if (reps === null) {
						errorMsg = "null response";
					} else if (reps.length > 0) {
						errorMsg = reps[0].nodeValue;
					} else {
						errorMsg = reps.nodeName;
					}
					throw new LucteriosException(GRAVE,
							"Erreur de parsing xml", this.m_XMLParameters,
							xml_text + "\nMsg:" + errorMsg);
				}
				return res_obs;
			}
		});

var ObserverFactoryRestImpl = ObserverFactoryImpl.extend({
	transfertFromServer : function(aExtension, aAction, aParam) {
		var val, self = this, web_file = aExtension + "/" + aAction;
		this.m_XMLParameters = web_file + "?";
		aParam.keys().forEach(function(key) {
			val = aParam.get(key);
			if (typeof val === 'string') {
				if (self.m_XMLParameters !== '') {
					self.m_XMLParameters += '&';
				}
				self.m_XMLParameters += key + "=" + val;
			} else {
				if (val instanceof Blob) {
					if (self.m_XMLParameters !== '') {
						self.m_XMLParameters += '&';
					}
					self.m_XMLParameters += key + "=" + val.name;
				}
			}
		});
		post_log("Ask " + self.m_XMLParameters);
		return this.mTransport.transfertFileFromServerString(web_file, aParam);
	}
});
