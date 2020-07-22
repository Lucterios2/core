/*global Class, HashMap, createGuid, FORM_MODAL, FORM_REFRESH, XMLSerializer, Singleton, unusedVariables */

var ObserverAbstract = Class.extend({

	mExtension : "",
	mAction : "",
	mTitle : "",
	mContext : new HashMap(),
	mJSON : null,
	mCloseAction : null,
	mRefresh : null,
	mGUIType : FORM_MODAL,
	mParent : null,
	mID : createGuid(),
	mGUI : null,

	getId : function() {
		return this.mID;
	},

	getParent : function() {
		return this.mParent;
	},

	setParent : function(aParent) {
		this.mParent = aParent;
	},

	init : function() {
		ObserverAbstract.ObserverName = "";
	},

	getObserverName : function() {
		return ObserverAbstract.ObserverName;
	},

	getSourceAction : function() {
		return this.mAction;
	},

	getSourceMethod : function() {
		return this.mMethod;
	},

	getSourceExtension : function() {
		return this.mExtension;
	},

	getContext : function() {
		return this.mContext;
	},

	getContent : function() {
		return this.mJSON;
	},

	getType : function() {
		return this.mType;
	},

	getContentText : function() {
		return JSON.stringify(this.mJSON);
	},

	getTitle : function() {
		return this.mTitle;
	},

	setSource : function(aExtension, aAction, aMethod) {
		this.mID = createGuid();
		this.mExtension = aExtension;
		this.mAction = aAction;
		this.mMethod = aMethod;
	},

	setCaption : function(aTitle) {
		this.mTitle = aTitle;
	},

	fillContext : function() {
		this.mContext = new HashMap();
		var contexts = this.mJSON.context, params, index;
		if (contexts) {
			params = Object.keys(contexts);
			for (index = 0; index < params.length; index++) {
				this.mContext.put(params[index], contexts[params[index]]);
			}
		}
	},

	setContent : function(aJSON) {
		this.mJSON = aJSON;
		if (this.mJSON !== null) {
			this.fillContext();
			if (this.mJSON.close) {
				if (this.mCloseAction === null) {
					this.mCloseAction = Singleton().CreateAction();
					this.mCloseAction.initialize(this, Singleton().Factory(), this.mJSON.close);
					this.mCloseAction.setCheckNull(false);
					this.mCloseAction.setClose(true);
					this.mCloseAction.setUsedContext(true);
				}
			}
			this.mRefresh = Singleton().CreateAction();
			this.mRefresh.initializeEx(this, Singleton().Factory(), this.getTitle(), this.getSourceExtension(), this.getSourceAction(), this.getSourceMethod());
			this.mRefresh.setFormType(FORM_REFRESH);
			this.mRefresh.setClose(false);
			this.mRefresh.setUsedContext(true);
		}
	},

	show : function(aTitle, aGUIType) {
		if (this.mTitle === '') {
			this.mTitle = aTitle;
		}
		this.mGUIType = aGUIType;
	},

	setActive : function(aIsActive) {
		unusedVariables(aIsActive);
	},

	closed : false,
	close : function(aMustRefreshParent) {
		if (!this.closed) {
			this.closed = true;
			this.closeEx();
			if (this.mCloseAction !== null) {
				this.mCloseAction.actionPerformed();
			}
			this.mCloseAction = null;
			var parent = this.getParent();
			if (aMustRefreshParent && (parent !== null)) {
				parent.refresh();
			}
			parent = null;
		}
	},

	refresh : function() {
		if (this.mRefresh !== null) {
			this.mRefresh.actionPerformed();
		}
	},

	closeEx : function() {
		return undefined;
	},

	getParameters : function(aCheckNull) {
		unusedVariables(aCheckNull);
		return new HashMap();
	},

	getGUI : function() {
		return this.mGUI;
	}

});

var ObserverGUI = ObserverAbstract.extend({

	mActions : null,

	setContent : function(aJSON) {
		this._super(aJSON);
		this.mActions = this.mJSON.actions;
	},

	buildButtons : function() {
		var btns = [], index, new_act;
		if (this.mActions) {
			for (index = 0; index < this.mActions.length; index++) {
				new_act = Singleton().CreateAction();
				new_act.initialize(this, Singleton().Factory(), this.mActions[index]);
				btns[btns.length] = new_act;
			}
		}
		return btns;
	},

	closeEx : function() {
		if (this.mGUI !== null) {
			this.mGUI.dispose();
		}
	},

	setActive : function(aIsActive) {
		if (this.mGUI !== null) {
			this.mGUI.setActive(aIsActive);
		}
	}

});
