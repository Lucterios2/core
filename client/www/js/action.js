/*global $, Class, createGuid, HashMap*/

var FORM_NOMODAL = 0;
var FORM_MODAL = 1;
var FORM_REFRESH = 2;

var SELECT_NONE = 1;
var SELECT_SINGLE = 0;
var SELECT_MULTI = 2;

var MNEMONIC_CHAR = '_';

var ActionAbstract = Class.extend({

	mOwner : null,
	mFactory : null,
	mExtension : '',
	mAction : '',
	mTitle : '',
	mID : '',
	mFormType : FORM_NOMODAL,
	mClose : true,
	mSelect : SELECT_NONE,
	mMethod : "GET",
	mIcon : '',
	mSizeIcon : '',
	mKeyStroke : '',
	mExtraParam : null,

	mCheckNull : true,
	mEnabled : true,
	mUsedContext : false,

	setEnabled : function(aEnabled) {
		this.mEnabled = aEnabled;
	},

	isEnabled : function() {
		return this.mEnabled;
	},

	initialize : function(aOwner, aFactory, aJSON) {
		var xmlparams, index;
		this.initializeEx(aOwner, aFactory, aJSON.text, aJSON.extension, aJSON.action, aJSON.method);
		if (aJSON.id !== null) {
			this.mID = aJSON.id;
		}
		this.mFormType = aJSON.modal ? parseInt(aJSON.modal, 10) : FORM_NOMODAL;
		this.mClose = ((aJSON.close ? parseInt(aJSON.close, 10) : 1) !== 0);
		this.mSelect = aJSON.unique ? parseInt(aJSON.unique, 10) : SELECT_NONE;
		this.mIcon = aJSON.icon || '';
		this.mSizeIcon = parseInt(aJSON.sizeicon, 10) || 0;
		this.mKeyStroke = aJSON.shortcut;
		if (aJSON.params) {
			xmlparams = Object.keys(aJSON.params);
			for (index = 0; index < xmlparams.length; index++) {
				this.mExtraParam.put(xmlparams[index], aJSON.params[xmlparams[index]]);
			}
		}
	},

	initializeEx : function(aOwner, aFactory, aTitle, aExtension, aAction, aMethod) {
		this.mOwner = aOwner;
		this.mFactory = aFactory;
		this.mTitle = aTitle || '';
		this.mExtraParam = new HashMap();
		this.mTitle = this.mTitle.replace(MNEMONIC_CHAR, '');
		this.mExtension = aExtension || '';
		this.mMethod = aMethod || "GET";
		this.mAction = aAction || '';
		this.mID = createGuid();
	},

	getOwner : function() {
		return this.mOwner;
	},

	getID : function() {
		return this.mID;
	},

	getTitle : function() {
		return this.mTitle;
	},

	getExtension : function() {
		return this.mExtension;
	},

	getAction : function() {
		return this.mAction;
	},

	getIcon : function() {
		return this.mIcon;
	},

	getFormType : function() {
		return this.mFormType;
	},

	getClose : function() {
		return this.mClose;
	},

	getSelect : function() {
		return this.mSelect;
	},

	getCheckNull : function() {
		return this.mCheckNull;
	},

	getUsedContext : function() {
		return this.mUsedContext;
	},

	setUsedContext : function(aUsedContext) {
		this.mUsedContext = aUsedContext;
	},

	setCheckNull : function(aCheckNull) {
		this.mCheckNull = aCheckNull;
	},

	setClose : function(aClose) {
		this.mClose = aClose;
	},

	setFormType : function(aFormType) {
		this.mFormType = aFormType;
	},

	getParameters : function() {
		var param;
		if (this.mOwner !== null) {
			if (this.mUsedContext) {
				param = this.mOwner.getContext();
			} else {
				param = this.mOwner.getParameters(this.mCheckNull);
			}
		} else {
			param = new HashMap();
		}
		if ((param !== null) && (this.mExtraParam !== null) && (this.mExtraParam.size() > 0)) {
			param.putAll(this.mExtraParam);
		}
		return param;
	},

	mustPerforme : function() {
		if (!this.mEnabled) {
			return false;
		}
		if ((this.mExtension === "") || (this.mAction === '')) {
			if ((this.mOwner !== null) && (this.mClose)) {
				this.mOwner.close(true);
			}
			return false;
		}
		return true;
	},

	actionPerformed : function() {
		if (this.mustPerforme()) {
			var param = this.getParameters();
			if (param !== null) {
				if ((this.mOwner !== null) && (this.mClose)) {
					this.mOwner.close(false);
				}
				if (this.mOwner !== null) {
					this.mOwner.setActive(false);
				}
				try {
					this.runAction(param);
				} finally {
					if ((this.mOwner !== null) && (this.mFormType !== FORM_REFRESH)) {
						this.mOwner.setActive(true);
					}
				}
			}
		}
	},

	get_button : function() {
		var result = {};
		result.text = this.getTitle();
		result.click = $.proxy(function() {
			this.actionPerformed();
		}, this);
		return result;
	}
});

var ActionImpl = ActionAbstract.extend({

	runAction : function(aParam) {
		var old_observrer = null, current_obs = null;
		if (this.mFormType === FORM_REFRESH) {
			old_observrer = this.getOwner();
		}
		current_obs = this.mFactory.callAction(this.mExtension, this.mAction, aParam, old_observrer, this.mMethod);

		if (!this.mUsedContext && (this.mOwner !== null)) {
			if ((this.mClose) || (this.mFormType === FORM_REFRESH)) {
				current_obs.setParent(this.mOwner.getParent());
			} else {
				current_obs.setParent(this.mOwner);
			}
		}
		current_obs.show(this.mTitle, this.mFormType);
	}
});

var ActionInt = ActionAbstract.extend({

	callback : null,

	mustPerforme : function() {
		return true;
	},

	runAction : function(aParam) {
		if (this.callback !== null) {
			this.callback(aParam);
		}
	}
});
