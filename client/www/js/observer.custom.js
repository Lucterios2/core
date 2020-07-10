/*global $,ObserverGUI,compBasic,HashMap,GUIManage,FORM_MODAL,showMessageDialog,LucteriosException,GRAVE,MINOR,createTable,createTab,compCaptcha,Singleton*/
/*global compImage,compLabelForm,compEdit,compFloat,compMemo,compXML,compMemoForm,compCheck,compGrid,compLink,compSelect,compCheckList,compButton,compDate,compTime,compDateTime,compPassword,compUpload,compdownload*/

var NULL_VALUE = 'NULL';

var ObserverCustom = ObserverGUI.extend({

	mCompList : new HashMap(),
	mDefaultBtn : '',

	get : function(key) {
		return this.mCompList[key];
	},

	getObserverName : function() {
		return "core.custom";
	},

	savefocusin : function(event) {
		$("#" + this.getId()).prop('fieldname', event.target.getAttribute("name"));
	},

	show : function(aTitle, aGUIType) {
		this._super(aTitle, aGUIType);
		this.setActive(true);

		var comp_idx, fieldname, gui_val, tabid, old_size;
		this.mGUI = new GUIManage(this.getId(), this.mTitle, this);
		this.mGUI.addcontent(this.getHtmlFromComponent(), this.buildButtons());
		this.mGUI.defaultbtn = this.mDefaultBtn;
		this.mGUI.showGUI(aGUIType === FORM_MODAL);
		for (comp_idx = 0; comp_idx < this.mCompList.size(); comp_idx++) {
			gui_val = this.mCompList.val(comp_idx);
			if (gui_val !== null) {
				gui_val.addAction();
				gui_val.getGUIComp().focusin($.proxy(this.savefocusin, this));
			}
		}
		this.gui_finalize(0);
		tabid = $("#" + this.getId()).prop('tabid');
		if (tabid !== undefined) {
			$("#" + this.getId()).find('ul > li:eq({0}) > a'.format(tabid)).click();
		} else {
			this.gui_finalize(1);
		}
		fieldname = $("#" + this.getId()).prop('fieldname');
		if (fieldname !== undefined) {
			$("#" + this.getId()).find("[name='{0}']:eq(0)".format(fieldname)).focus();
		}
		old_size=$("#"+this.getId()).data('old_size');
		if ((old_size !== undefined) && (old_size !== null)) {
			$("#"+this.getId()).data('old_size', null);
			this.mGUI.fullscreen();
		} else {
			this.mGUI.reloadSize();
		}

	},

	checkCompoundValid : function() {
		var cmp, comp_idx;
		try {
			for (comp_idx = 0; comp_idx < this.mCompList.size(); comp_idx++) {
				cmp = this.mCompList.val(comp_idx);
				cmp.checkValid();
			}
		} catch (lctept) {
			if (cmp !== null) {
				cmp.getGUIComp().focus();
			}
			if (lctept.message !== '') {
				showMessageDialog(lctept.message, this.getTitle());
			}
			return false;
		}
		return true;
	},

	getParameters : function(aCheckNull) {
		if (!aCheckNull || this.checkCompoundValid()) {
			var params = new HashMap(), comp_idx;
			params.putAll(this.mContext);
			for (comp_idx = 0; comp_idx < this.mCompList.size(); comp_idx++) {
				this.mCompList.val(comp_idx).fillValue(params);
			}
			return params;
		}
		return null;
	},

	getHtmlFromComponent : function() {
		var compArray = [], hasTabs = false, tabs = [], tabContent = [], actualTab = -1, compType, components, iComp, component, comp, html;

		this.mCompList = new HashMap();
		components = this.mJSON.comp;
		if (components) {
			for (iComp = 0; iComp < components.length; iComp++) {
				component = components[iComp];
				component.value = this.mJSON.data[component.name];
				compType = component.component;
				if (compType !== undefined) {
					switch (compType) {
					case "IMAGE":
						comp = new compImage(this);
						break;
					case "LABELFORM":
					case "LABEL":
						comp = new compLabelForm(this);
						break;
					case "EDIT":
						comp = new compEdit(this);
						break;
					case "FLOAT":
						comp = new compFloat(this);
						break;
					case "MEMO":
						comp = new compMemo(this);
						break;
					case "XML":
						comp = new compXML(this);
						break;
					case "CHECK":
						comp = new compCheck(this);
						break;
					case "GRID":
						comp = new compGrid(this);
						break;
					case "LINK":
						comp = new compLink(this);
						break;
					case "SELECT":
						comp = new compSelect(this);
						break;
					case "CHECKLIST":
						comp = new compCheckList(this);
						break;
					case "BUTTON":
						comp = new compButton(this);
						break;
					case "DATE":
						comp = new compDate(this);
						break;
					case "TIME":
						comp = new compTime(this);
						break;
					case "DATETIME":
						comp = new compDateTime(this);
						break;
					case "PASSWD":
						comp = new compPassword(this);
						break;
					case "UPLOAD":
						comp = new compUpload(this);
						break;
					case "DOWNLOAD":
						comp = new compdownload(this);
						break;
					case "CAPTCHA":
						comp = new compCaptcha(this);
						break;
					case "TAB":
						hasTabs = true;
						actualTab++;
						tabs[actualTab] = component.value;
						tabContent[actualTab] = [];
						break;
					default:
						throw new LucteriosException(GRAVE, "Unknown composant:" + compType);
					}
					if (compType !== "TAB") {
						comp.initial(component);
						if (hasTabs) {
							if (tabContent[actualTab][comp.y] === undefined) {
								tabContent[actualTab][comp.y] = [];
							}
							tabContent[actualTab][comp.y][comp.x] = comp;
						} else {
							if (compArray[comp.y] === undefined) {
								compArray[comp.y] = [];
							}
							compArray[comp.y][comp.x] = comp;
						}
						this.mCompList.put(comp.name, comp);
					}
				}
			}
		}

		html = createTable(compArray);
		if (hasTabs) {
			html += createTab(tabs, tabContent);
		}
		return html;
	},

	gui_finalize : function(tabid) {
		var cmp, comp_idx;
		for (comp_idx = 0; comp_idx < this.mCompList.size(); comp_idx++) {
			cmp = this.mCompList.val(comp_idx);
			if (cmp.tab === tabid) {
				cmp.gui_finalize();
			}
		}
	}

});

// Generic
var compGeneric = compBasic.extend({
	name : "",
	VMin : 0,
	HMin : 0,
	tab : 0,
	description : "",
	owner : null,
	tag : '',
	descComp : null,

	init : function(aOwner) {
		this.owner = aOwner;
	},

	get_id : function() {
		return "{0}_{1}".format(this.owner.getId(), this.name);
	},

	getGUIComp : function() {
		return $("#" + this.owner.getId()).find("{0}[name='{1}']:eq(0)".format(this.tag, this.name));
	},

	setEnabled : function(isEnabled) {
		this.getGUIComp().prop("disabled", !isEnabled);
		if (this.descComp !== null) {
			this.descComp.setEnabled(isEnabled);
		}
	},

	setVisible : function(isVisible) {
		var cell_cont = this.getGUIComp()[0];
		while ((cell_cont.nodeName !== 'TD') && (cell_cont.parentNode !== null) && (cell_cont.parentNode !== cell_cont)) {
			cell_cont = cell_cont.parentNode;
		}
		if (cell_cont.style !== null) {
			if (isVisible) {
				cell_cont.style.display = null;
				cell_cont.style.fontSize = null;
			} else {
				cell_cont.style.display = "none";
				cell_cont.style.fontSize = "0px";
			}
		}
		if (this.descComp !== null) {
			this.descComp.setVisible(isVisible);
		}
	},

	requestFocus : function() {
		this.getGUIComp().focus();
	},

	getValue : function() {
		return this.getGUIComp().val();
	},

	initialVal : function() {
		return null;
	},

	setValue : function(jsonvalue) {
		this.initial(jsonvalue);
		this.getGUIComp().val(this.initialVal());
	},

	initial : function(component) {
		if (this.name === '') {
			this.name = component.name;
			this.description = component.description || '';
			this.description = this.description.replace(/%E9/g, 'é').replace(/%E8/g, 'è').replace(/%EA/g, 'ê');
			this.description = this.description.replace(/%[D-F][0-9A-F]/g, '?');
			this.tab = component.tab;
			this.x = component.x;
			this.y = component.y;
			this.vmin = parseInt(component.VMin, 10) || -1;
			this.hmin = parseInt(component.HMin, 10) || -1;
			this.colspan = component.colspan;
			this.rowspan = component.rowspan;
			this.needed = component.needed;
			this.is_null = !this.needed && (component.value === NULL_VALUE);
		}
	},

	getAttribHtml : function(args, isJustify) {
		args.name = this.name;
		args.id = this.get_id();
		args.description = this.description;
		if (args.cssclass === undefined) {
			args.cssclass = '';
		}
		args.cssclass += ' class_controle';
		if (isJustify) {
			args.cssclass += ' lctjustify';
		}
		if (this.hmin !== -1) {
			if (args.style === undefined) {
				args.style = "";
			}
			args.style += "min-width: {0}px;".format(this.hmin);
		}
		if (this.vmin !== -1) {
			if (args.style === undefined) {
				args.style = "";
			}
			args.style += "min-height: {0}px;".format(this.vmin);
		}
		var html = "", element;
		for (element in args) {
			if (args.hasOwnProperty(element)) {
				html += ' {0}="{1}"'.format(element.replace('cssclass', 'class'), args[element]);
			}
		}
		return html;
	},

	getHtml : function() {
		var html = "<lct-cell>";
		if (this.description !== '') {
			html += "<label for='{0}'>".format(this.get_id());
			html += this.description;
			html += "</label>";
			html += "<lct-ctrl>";
			html += this.get_Html();
			html += "</lct-ctrl>";
		} else {
			html += this.get_Html();
		}
		html += "</lct-cell>";
		return html;
	},

	getBuildHtml : function(args, isJustify, isClose) {
		var html = "<" + this.tag + this.getAttribHtml(args, isJustify);
		if (isClose) {
			html += '/';
		}
		html += '>';
		return html;
	},

	checkValid : function() {
		var msg_text;
		if (this.needed && ((this.getValue() === null) || (this.getValue() === ''))) {
			msg_text = Singleton().getTranslate("This field is needed!");
			if (this.description.length > 0) {
				msg_text = Singleton().getTranslate("The field '{0}' is needed!").format(decodeURIComponent(this.description.replace(/\+/g, ' ')));
			}
			throw new LucteriosException(MINOR, msg_text);
		}
		return;
	},

	fillValue : function(params) {
		if (this.initialVal() !== null) {
			params.put(this.name, this.getValue());
		}
	},

	addAction : function() {
		return undefined;
	},

	gui_finalize : function() {
		return;
	}
});
