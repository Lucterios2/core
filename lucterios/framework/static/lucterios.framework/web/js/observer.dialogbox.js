/*global ObserverGUI, Singleton, compBasic, GUIManage, createTable, unusedVariables*/

var ObserverDialogBox = ObserverGUI.extend({

	getObserverName : function() {
		return "core.dialogbox";
	},

	setContent : function(aDomXmlContent) {
		this._super(aDomXmlContent);
		var xml_text = this.mDomXmlContent.getElementsByTagName("TEXT")[0];
		this.mText = xml_text.getTextFromXmlNode();
		this.mType = xml_text.getXMLAttributInt("type", 0);
	},

	show : function(aTitle, aGUIType) {
		this._super(aTitle, aGUIType);

		var image_name = '', table = [];
		switch (this.mType) {
		case 2:
			image_name = "static/lucterios.CORE/images/confirm.png";
			break;
		case 3:
			image_name = "static/lucterios.CORE/images/warning.png";
			break;
		case 4:
			image_name = "static/lucterios.CORE/images/error.png";
			break;
		default:
			image_name = "static/lucterios.CORE/images/info.png";
			break;
		}
		image_name = Singleton().Transport().getIconUrl(image_name);
		this.mText = this.mText.convertLuctoriosFormatToHtml();

		table[0] = [];
		table[0][0] = new compBasic("<img src='" + image_name + "' alt='"
				+ image_name + "'></img>");
		table[0][1] = new compBasic("<label>" + this.mText + "</label>");

		this.mGUI = new GUIManage(this.getId(), this.mTitle, this);
		this.mGUI.addcontent(createTable(table), this.buildButtons());
		this.mGUI.showGUI(true);
	},

	getParameters : function(aCheckNull) {
		unusedVariables(aCheckNull);
		return this.mContext;
	}

});

var showMessageDialog = function(aText, aTitle) {
	var obs = new ObserverDialogBox();
	obs.mType = 0;
	obs.mText = aText;
	obs.show(aTitle);
};
