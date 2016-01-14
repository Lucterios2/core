/*global Class, HashMap, createGuid, FORM_MODAL, FORM_REFRESH, XMLSerializer, Singleton, unusedVariables */

var ObserverAbstract = Class
		.extend({

			mExtension : "",
			mAction : "",
			mTitle : "",
			mContext : new HashMap(),
			mDomXmlContent : null,
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

			getSourceExtension : function() {
				return this.mExtension;
			},

			getContext : function() {
				return this.mContext;
			},

			getContent : function() {
				return this.mDomXmlContent;
			},

			getType : function() {
				return this.mType;
			},

			getContentText : function() {
				var result = "", node_idx, node, serializer;
				for (node_idx = 0; node_idx < this.mDomXmlContent.childNodes.length; node_idx++) {
					node = this.mDomXmlContent.childNodes[node_idx];
					if (node.nodeName !== 'CONTEXT') {
						if (XMLSerializer !== undefined) {
							serializer = new XMLSerializer();
							result += serializer.serializeToString(node);
						} else if (node.xml) {
							result += node.xml;
						}
					}
				}
				return result;
			},

			getTitle : function() {
				return this.mTitle;
			},

			setSource : function(aExtension, aAction) {
				this.mID = createGuid();
				this.mExtension = aExtension;
				this.mAction = aAction;
			},

			setCaption : function(aTitle) {
				this.mTitle = aTitle;
			},

			fillContext : function() {
				this.mContext = new HashMap();
				var xmlcontexts = this.mDomXmlContent
						.getElementsByTagName("CONTEXT"), xmlparams, index;
				if (xmlcontexts.length > 0) {
					xmlparams = xmlcontexts[0].getElementsByTagName("PARAM");
					for (index = 0; index < xmlparams.length; index++) {
						this.mContext
								.put(
										xmlparams[index].getAttribute("name"),
										xmlparams[index].childNodes.length > 0 ? xmlparams[index].childNodes[0].nodeValue
												: '');
					}
				}
			},

			setContent : function(aDomXmlContent) {
				this.mDomXmlContent = aDomXmlContent;
				if (this.mDomXmlContent !== null) {
					this.fillContext();
					var xml_item_closes = this.mDomXmlContent
							.getElementsByTagName("CLOSE_ACTION"), xml_items, action_idx;
					if (xml_item_closes.length > 0) {
						xml_items = xml_item_closes[0]
								.getElementsByTagName("ACTION");
						for (action_idx = 0; (this.mCloseAction === null)
								&& (action_idx < xml_items.length); action_idx++) {
							this.mCloseAction = Singleton().CreateAction();
							this.mCloseAction.initialize(this, Singleton()
									.Factory(), xml_items[action_idx]);
							this.mCloseAction.setCheckNull(false);
							this.mCloseAction.setClose(true);
							this.mCloseAction.setUsedContext(true);
						}
					}
					this.mRefresh = Singleton().CreateAction();
					this.mRefresh.initializeEx(this, Singleton().Factory(),
							this.getTitle(), this.getSourceExtension(), this
									.getSourceAction());
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

	setContent : function(aDomXmlContent) {
		this._super(aDomXmlContent);
		this.mActions = this.mDomXmlContent.getFirstTag("ACTIONS");
	},

	buildButtons : function() {
		var btns = [], xml_actions, index, new_act;
		if (this.mActions !== null) {
			xml_actions = this.mActions.getElementsByTagName("ACTION");
			for (index = 0; index < xml_actions.length; index++) {
				new_act = Singleton().CreateAction();
				new_act.initialize(this, Singleton().Factory(),
						xml_actions[index]);
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
