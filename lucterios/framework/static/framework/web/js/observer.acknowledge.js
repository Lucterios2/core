/*global ObserverAbstract, Singleton, HashMap, unusedVariables */

var ObserverAcknowledge = ObserverAbstract.extend({

	mRedirectAction : null,

	getRedirectAction : function() {
		return this.mRedirectAction;
	},

	setContent : function(aDomXmlContent) {
		this._super(aDomXmlContent);
		var acts = this.mDomXmlContent.getElementsByTagName("ACTION");
		if (acts.length > 0) {
			this.mRedirectAction = Singleton().CreateAction();
			this.mRedirectAction.initialize(this, Singleton().Factory(),
					acts[0]);
			this.mRedirectAction.setClose(true);
		} else {
			this.mRedirectAction = null;
		}
	},

	getObserverName : function() {
		return "core.acknowledge";
	},

	getParameters : function(aCheckNull) {
		unusedVariables(aCheckNull);
		var requete = new HashMap();
		requete.putAll(this.mContext);
		return requete;
	},

	show : function(aTitle, aGUIType) {
		this._super(aTitle, aGUIType);
		this.setActive(true);
		if (this.mRedirectAction !== null) {
			this.mRedirectAction.actionPerformed();
		}
		this.close(this.mRedirectAction === null);
	}

});
