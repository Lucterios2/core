/*global $, Class, createGuid, HashMap*/

var FORM_NOMODAL = 0;
var FORM_MODAL = 1;
var FORM_REFRESH = 2;

var SELECT_NONE = 1;
var SELECT_SINGLE = 0;
var SELECT_MULTI = 2;

var MNEMONIC_CHAR = '_';

var ActionAbstract = Class
		.extend({

			mOwner : null,
			mFactory : null,
			mExtension : '',
			mAction : '',
			mTitle : '',
			mMnemonic : '',
			mID : '',
			mFormType : FORM_NOMODAL,
			mClose : true,
			mSelect : SELECT_NONE,
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

			initialize : function(aOwner, aFactory, aXml) {
				var xmlparams, index;
				this.initializeEx(aOwner, aFactory, aXml.getTextFromXmlNode(),
						aXml.getAttribute("extension"), aXml
								.getAttribute("action"));
				if (aXml.getAttribute("id") !== null) {
					this.mID = aXml.getAttribute("id");
				}
				this.mFormType = aXml.getXMLAttributInt("modal", FORM_NOMODAL);
				this.mClose = (aXml.getXMLAttributInt("close", 1) !== 0);
				this.mSelect = aXml.getXMLAttributInt("unique", SELECT_NONE);
				this.mIcon = aXml.getAttribute("icon");
				if (this.mIcon === null) {
					this.mIcon = '';
				}
				this.mSizeIcon = aXml.getXMLAttributInt("sizeicon", 0);
				this.mKeyStroke = aXml.getAttribute("shortcut");
				xmlparams = aXml.getElementsByTagName("PARAM");
				for (index = 0; index < xmlparams.length; index++) {
					this.mExtraParam
							.put(
									xmlparams[index].getAttribute("name"),
									xmlparams[index].childNodes.length > 0 ? xmlparams[index].childNodes[0].nodeValue
											: '');
				}
			},

			initializeEx : function(aOwner, aFactory, aTitle, aExtension,
					aAction) {
				this.mOwner = aOwner;
				this.mFactory = aFactory;
				this.mTitle = aTitle;
				this.mExtraParam = new HashMap();
				var pos = this.mTitle.indexOf(MNEMONIC_CHAR);
				if ((pos !== -1) && (this.mTitle.length > 0)) {
					this.mMnemonic = this.mTitle.charAt(this.mTitle
							.indexOf(MNEMONIC_CHAR) + 1);
				}
				this.mTitle = this.mTitle.replace(MNEMONIC_CHAR, '');
				this.mExtension = aExtension;
				if (this.mExtension === null) {
					this.mExtension = '';
				}
				this.mAction = aAction;
				if (this.mAction === null) {
					this.mAction = '';
				}
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

			getMnemonic : function() {
				return this.mMnemonic;
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
				if ((param !== null) && (this.mExtraParam !== null)
						&& (this.mExtraParam.size() > 0)) {
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
							if ((this.mOwner !== null)
									&& (this.mFormType !== FORM_REFRESH)) {
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
		current_obs = this.mFactory.callAction(this.mExtension, this.mAction,
				aParam, old_observrer);

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
