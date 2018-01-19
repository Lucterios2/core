/*global $,LucteriosException,Uint8Array,CRITIC,IMPORTANT,GRAVE,MINOR,compGeneric,Class,Singleton,post_log,SELECT_NONE,SELECT_SINGLE,SELECT_MULTI,zip,NULL_VALUE,unusedVariables*/
/*jslint regexp: true */

// image
var compImage = compGeneric.extend({
	height : 0,
	width : 0,
	src : "",
	type : "",

	initial : function(component) {
		this._super(component);
		this.height = component.height;
		this.width = component.width;
		this.src = component.value;
		this.type = component.type;
		this.needed = 0;
		this.tag = 'img';
	},

	checkValid : function() {
		return;
	},

	get_Html : function() {
		var src_img = this.src;
		if (this.type === '') {
			src_img = Singleton().Transport().getIconUrl(this.src + "?val=" + Math.floor(Math.random() * 1000));
		} else {
			if (this.src.substring(0, 10) === 'data:image') {
				src_img = this.src;
			} else {
				src_img = 'data:image/{0};base64,{1}'.format(this.type, this.src);
			}
		}
		return this.getBuildHtml({
			'src' : src_img
		}, false, true);
	}
});

// label formaté
var compLabelForm = compGeneric.extend({
	label : "",

	initial : function(component) {
		this._super(component);
		this.needed = 0;

		this.label = component.value.convertLuctoriosFormatToHtml();
		this.tag = 'span';
	},

	checkValid : function() {
		return;
	},

	get_Html : function() {
		return this.getBuildHtml({}, false, false) + this.label + '</span>';
	}
});

var compCaptcha = compGeneric.extend({
	num1 : 0,
	num2 : 0,
	operation : 0,
	operation_txt : '+',
	total : 0,

	initial : function(component) {
		this._super(component);
		this.tag = 'input';
		this.num1 = Math.floor((Math.random() * 10) + 1);
		this.num2 = Math.floor((Math.random() * 10) + 1);
		this.operation = Math.floor((Math.random() * 3) + 1);
		if (this.operation === 0) {
			this.total = this.num1 + this.num2;
			this.operation_txt = '+';
		} else if ((this.operation === 1) && (this.num2 < this.num1)) {
			this.total = this.num1 - this.num2;
			this.operation_txt = '-';
		} else {
			this.total = this.num1 * this.num2;
			this.operation_txt = 'x';
		}
	},

	get_Html : function() {
		var args = {
			'type' : "text",
			'cssclass' : 'lctcapcha'
		};
		args.value = '';
		return "{0} {1} {2} = {3}".format(this.num1, this.operation_txt, this.getBuildHtml(args, false, true), this.total);
	},

	initialVal : function() {
		return this.value;
	},

	checkValid : function() {
		var msg_text, inputVal;
		this._super();
		inputVal = parseInt('0' + this.getGUIComp().val(), 10);
		if (inputVal !== this.num2) {
			msg_text = Singleton().getTranslate("Captcha wrong!");
			throw new LucteriosException(MINOR, msg_text);
		}
		return;
	}
});

// event
var compAbstractEvent = compGeneric.extend({
	action : null,
	java_script_content : null,

	initial : function(component) {
		this._super(component);
		if (component.action) {
			this.action = Singleton().CreateAction();
			this.action.initialize(this.owner, Singleton().Factory(), component.action);
			this.action.setCheckNull(false);
		}
		this.java_script_content = component.javascript || '';
		if (component.is_default) {
			this.owner.mDefaultBtn = "{0}[name='{1}']".format(this.tag, this.name);
		}
	},

	addAction : function() {
		return undefined;
	},

	get_act_function : function() {
		var act_function = null, adder = null, init_val;
		if ((this.java_script_content !== '') || (this.action !== null)) {
			post_log("java script :" + this.java_script_content);
			act_function = function() {
				if (this.java_script_content !== '') {
					adder = new Function("current", "parent", this.java_script_content); /*
																							 * jshint
																							 * -W054
																							 */
					adder(this, this.owner);
				}
				if (this.action !== null) {
					if (this.is_null === true) {
						init_val = NULL_VALUE;
					} else {
						init_val = this.initialVal();
					}
					if (this.getValue() !== init_val) {
						this.action.actionPerformed();
					}
				}
			};
			if (this.java_script_content !== '') {
				adder = new Function("current", "parent", this.java_script_content); /*
																						 * jshint
																						 * -W054
																						 */
				adder(this, this.owner);
			}
		}
		return act_function;
	},

	addActionEx : function(typeAct) {
		var act_function = this.get_act_function(), gui_comp;
		if (act_function !== null) {
			gui_comp = this.getGUIComp();
			switch (typeAct) {
			case 0: // focus
				gui_comp.focusout($.proxy(act_function, this));
				break;
			case 1: // click
				gui_comp.click($.proxy(act_function, this));
				break;
			case 2: // change
				gui_comp.change($.proxy(act_function, this));
				break;
			default:
				throw new LucteriosException(CRITIC, "Bad type!");
			}
		}
		this.addActionNull(act_function);
	},

	addActionNull : function(act_function) {
		var nullcheck;
		if (this.needed === false) {
			nullcheck = $("#" + this.owner.getId()).find("input[name='nullcheck_{0}']:eq(0)".format(this.name));
			nullcheck.change($.proxy(function() {
				if (act_function !== null) {
					$.proxy(act_function, this)();
				}
				this.setEnabled(!nullcheck[0].checked);
			}, this));
			if (this.is_null) {
				this.setEnabled(false);
			}
		}
	},

	addnullcheck : function() {
		var res = '', valcheck = '';
		if (this.needed === false) {
			if (this.is_null === true) {
				valcheck = 'checked = "checked"';
			}
			res = '<input class="class_checknull" type="checkbox" name="nullcheck_{0}" {1}/>'.format(this.name, valcheck);
		}
		return res;
	},

	is_return_null : function() {
		var res = false, nullcheck;
		if (this.needed === false) {
			nullcheck = $("#" + this.owner.getId()).find("input[name='nullcheck_{0}']:eq(0)".format(this.name));
			res = nullcheck[0].checked;
		}
		return res;
	}
});

// bouton
var compButton = compAbstractEvent.extend({
	clickName : '',
	clickValue : '',
	isMini : false,
	hasBeenClicked : false,
	btnaction : null,
	tag : 'button',

	initial : function(component) {
		this._super(component);
		this.isMini = component.is_mini;
		this.needed = 0;
		this.tag = 'button';
	},

	actionPerformed : function() {
		this.hasBeenClicked = true;
		this.btnaction.actionPerformed();
		this.hasBeenClicked = false;
	},

	addAction : function() {
		this.addActionEx(1);
	},

	checkValid : function() {
		return;
	},

	get_Html : function() {
		if (this.action !== null) {
			var arg = {}, title, btn_icon;
			this.btnaction = this.action;
			this.action = this;
			if (this.isMini) {
				arg.cssclass = 'lctbtnmini';
			} else {
				arg.cssclass = 'lctbtn';
			}
			if (!this.isMini || (this.btnaction.getIcon() === '')) {
				title = this.btnaction.getTitle();
			} else {
				title = '';
			}
			if (this.btnaction.getIcon() !== '') {
				btn_icon = Singleton().Transport().getIconUrl(this.btnaction.getIcon());
				title = '<img src="{0}" style="max-width:32px"/>'.format(btn_icon) + title;
			}
			return this.getBuildHtml(arg, false, false) + title + "</button>";
		}
		return '';
	},

	setSelectType : function(aSelectType) {
		var enabled = false;
		switch (aSelectType) {
		case SELECT_NONE:
			enabled = (this.btnaction.mSelect === SELECT_NONE);
			break;
		case SELECT_SINGLE:
			enabled = true;
			break;
		case SELECT_MULTI:
			enabled = (this.btnaction.mSelect !== SELECT_SINGLE);
			break;
		default:
			throw new LucteriosException(CRITIC, "Bad type!");
		}
		this.setEnabled(enabled);
	}

});

// case à cocher
var compCheck = compAbstractEvent.extend({
	// generiques
	checked : 0,
	tag : 'input',

	initial : function(component) {
		this._super(component);

		var val = component.value;
		this.checked = (parseInt(val, 10) === 1) || (val === 'o');
		this.tag = 'input';
	},

	get_Html : function() {
		var args = {
			'type' : "checkbox"
		};
		if (this.checked) {
			args.checked = "checked";
		}
		return this.getBuildHtml(args, false, true);
	},

	getValue : function() {
		var comp = this.getGUIComp();
		return comp[0].checked;
	},

	setValue : function(jsonvalue) {
		this.initial(jsonvalue);
		this.getGUIComp()[0].checked = this.initialVal();
	},

	initialVal : function() {
		return this.checked;
	},

	checkValid : function() {
		return;
	},

	fillValue : function(params) {
		if (this.getValue()) {
			params.put(this.name, 'o');
		} else {
			params.put(this.name, 'n');
		}
	},

	addAction : function() {
		this.addActionEx(2);
	}
});

var compLink = compGeneric.extend({
	link : "",
	label : "",
	tag : 'a',

	initial : function(component) {
		this._super(component);
		this.label = component.value.convertLuctoriosFormatToHtml();
		this.link = component.link;
		this.needed = 0;
		this.tag = 'a';
	},

	checkValid : function() {
		return;
	},

	get_Html : function() {
		return this.getBuildHtml({
			'href' : this.link,
			'target' : '_blank'
		}, false, false) + this.label + '</a>';
	}
});

var compEdit = compAbstractEvent.extend({
	value : "",
	mask : null,
	size : -1,
	tag : 'input',

	initial : function(component) {
		var regex;
		this._super(component);
		this.value = component.value;
		this.size = component.size || -1;
		regex = component.reg_expr;
		if (regex !== '') {
			this.mask = new RegExp(regex, 'i');
		}
		this.tag = 'input';
	},

	get_Html : function() {
		var args = {
			'type' : "text"
		};
		args.value = this.initialVal();
		return this.getBuildHtml(args, true, true);
	},

	initialVal : function() {
		return this.value;
	},

	checkValid : function() {
		var msg_text, inputVal;
		this._super();
		if (this.mask !== null) {
			inputVal = this.getGUIComp().val();
			if (!this.mask.test(inputVal)) {
				msg_text = Singleton().getTranslate("Invalid format!");
				throw new LucteriosException(MINOR, msg_text);
			}
		} else if (this.size !== -1) {
			inputVal = this.getGUIComp().val().trim();
			if (inputVal.length > this.size) {
				msg_text = Singleton().getTranslate("Size too long!");
				throw new LucteriosException(MINOR, msg_text);
			}
		}
		return;
	},

	addAction : function() {
		this.addActionEx(0);
		if ((this.mask !== null) || (this.size !== -1)) {
			this.getGUIComp().keyup($.proxy(function() {
				var inputVal = this.getGUIComp().val();
				if (((this.mask !== null) && !this.mask.test(inputVal)) || ((this.size !== -1) && (inputVal.trim().length > this.size))) {
					this.getGUIComp().css({
						'background-color' : 'red'
					});
				} else {
					this.getGUIComp().css({
						'background-color' : 'white'
					});
				}
			}, this));
		}
	}

});

var compFloat = compAbstractEvent.extend({
	value : "",
	min : 0,
	max : 1000,
	prec : 1,
	tag : 'input',

	initial : function(component) {
		this._super(component);
		var text_value = '', nb_dec = (component.prec || 0), dec_i;
		if (this.is_null === false) {
			text_value = component.value;
		}
		if (text_value === '') {
			text_value = '0';
		}
		this.value = parseFloat(text_value);
		this.min = component.min ? parseFloat(component.min) : 0.0;
		this.max = component.max ? parseFloat(component.max) : 1000.0;
		this.prec = 1;
		for (dec_i = 0; dec_i < nb_dec; dec_i++) {
			this.prec = this.prec / 10;
		}
		this.tag = 'input';
	},

	get_Html : function() {
		var args = {
			'type' : "text"
		};
		args.value = this.initialVal();
		return this.addnullcheck() + this.getBuildHtml(args, true, true);
	},

	getValue : function() {
		var val_num;
		if (this.is_return_null() === true) {
			return NULL_VALUE;
		}
		val_num = this.getGUIComp().val();
		val_num = val_num.replace(",", ".");
		val_num = Math.max(val_num, this.min);
		val_num = Math.min(val_num, this.max);
		return "{0}".format(val_num);
	},

	initialVal : function() {
		return "{0}".format(this.value);
	},

	setEnabled : function(isEnabled) {
		try {
			if (isEnabled === true) {
				this.getGUIComp().spinner("enable");
			} else {
				this.getGUIComp().spinner("disable");
			}
		} catch (lctept) {
			this.getGUIComp().prop("disabled", !isEnabled);
		}
	},

	addAction : function() {
		this.getGUIComp().spinner({
			step : this.prec,
			min : this.min,
			max : this.max,
			numberFormat : "n"
		});
		this.addActionEx(0);
	}

});

var editorHypertext = Class.extend({
	name : '',
	with_hypertext : false,
	submenus : {},
	init : function(aOwnerId, aName, aWith_hypertext, aSub_menu) {
		var isub_menu, sub_menu;
		this.ownerId = aOwnerId;
		this.name = aName;
		this.with_hypertext = aWith_hypertext;
		this.submenus = {};
		for (isub_menu = 0; isub_menu < aSub_menu.length; isub_menu++) {
			sub_menu = aSub_menu[isub_menu];
			this.submenus[sub_menu[1]] = {
				name : sub_menu[0]
			};
		}
	},
	getGUIComp : function() {
		return $("#" + this.ownerId).find("textarea[name='{0}']:eq(0)".format(this.name));
	},
	get_Html : function(attribut, value) {
		var html = "";
		if (this.with_hypertext) {
			html += '<div class="ui-widget-header">';
			html += '<img id="bold_{0}" src="images/bold.png" class="memobtn">'.format(this.name);
			html += '<img id="italic_{0}" src="images/italic.png" class="memobtn">'.format(this.name);
			html += '<img id="underline_{0}" src="images/underline.png" class="memobtn">'.format(this.name);
			html += '<img id="black_{0}" src="images/black.png" class="memobtn">'.format(this.name);
			html += '<img id="blue_{0}" src="images/blue.png" class="memobtn">'.format(this.name);
			html += '<img id="red_{0}" src="images/red.png" class="memobtn">'.format(this.name);
			html += '<img id="green_{0}" src="images/green.png" class="memobtn">'.format(this.name);
			html += '</div>';
		}
		html += '<textarea ' + attribut + '>' + value + '</textarea>';
		return html;
	},
	addEditorAction : function() {
		var area_name = "textarea[name='{0}']".format(this.name), self = this;
		if (Object.keys(this.submenus).length > 0) {
			$("#" + this.ownerId).contextMenu({
				selector : area_name,
				items : this.submenus,
				callback : function(key, options) {
					unusedVariables(options);
					var cursorPos, val_area, variable_text, textBefore, textAfter;
					variable_text = "#" + key;
					cursorPos = self.getGUIComp().prop('selectionStart');
					val_area = self.getGUIComp().val();
					textBefore = val_area.substring(0, cursorPos);
					textAfter = val_area.substring(cursorPos, val_area.length);
					self.getGUIComp().val(textBefore + variable_text + textAfter);
				}
			});
		}
		$("#bold_{0}".format(this.name)).click(function() {
			self.add_text_tag('b', '');
		});
		$("#italic_{0}".format(this.name)).click(function() {
			self.add_text_tag('i', '');
		});
		$("#underline_{0}".format(this.name)).click(function() {
			self.add_text_tag('u', '');
		});
		$("#black_{0}".format(this.name)).click(function() {
			self.add_text_tag('font', 'color="black"');
		});
		$("#red_{0}".format(this.name)).click(function() {
			self.add_text_tag('font', 'color="red"');
		});
		$("#blue_{0}".format(this.name)).click(function() {
			self.add_text_tag('font', 'color="blue"');
		});
		$("#green_{0}".format(this.name)).click(function() {
			self.add_text_tag('font', 'color="green"');
		});
	},

	add_text_tag : function(tagname, extra) {
		var cursorPosBegin, cursorPosEnd, val_area, select_val, textBefore, textAfter;
		if (extra !== '') {
			extra = ' ' + extra;
		}
		cursorPosBegin = this.getGUIComp().prop('selectionStart');
		cursorPosEnd = this.getGUIComp().prop('selectionEnd');
		val_area = this.getGUIComp().val();
		textBefore = val_area.substring(0, cursorPosBegin);
		select_val = val_area.substring(cursorPosBegin, cursorPosEnd);
		textAfter = val_area.substring(cursorPosEnd, val_area.length);
		this.getGUIComp().val("{0}{[{1}{2}]}{3}{[/{1}]}{4}".format(textBefore, tagname, extra, select_val, textAfter));
	}

});

var compMemo = compAbstractEvent.extend({
	value : "",
	tag : 'textarea',

	initial : function(component) {
		this._super(component);
		this.value = component.value.replace(/\{\[newline\]\}/g, "\n").replace(/\{\[br\/\]\}/g, "\n");
		this.editor = new editorHypertext(this.owner.getId(), this.name, component.with_hypertext, component.submenu);
		this.tag = 'textarea';
	},

	get_Html : function() {
		return this.editor.get_Html(this.getAttribHtml({}, true), this.initialVal());
	},

	initialVal : function() {
		return this.value;
	},

	fillValue : function(params) {
		var val = this.getValue();
		params.put(this.name, val.replace(/\n/g, '{[br/]}'));
	},

	addAction : function() {
		this.addActionEx(0);
		this.editor.addEditorAction();
	}
});

var compXML = compAbstractEvent.extend({
	value : "",
	tag : 'textarea',

	initial : function(component) {
		this._super(component);
		this.value = component.value;
		this.editor = new editorHypertext(this.owner.getId(), this.name, 1, component.submenu);
		this.tag = 'textarea';
	},

	get_Html : function() {
		return this.editor.get_Html(this.getAttribHtml({}, true), this.initialVal());
	},

	initialVal : function() {
		return this.value;
	},

	fillValue : function(params) {
		var val = this.getValue();
		params.put(this.name, val);
	},

	addAction : function() {
		this.addActionEx(0);
		this.editor.addEditorAction();
	}
});

var compPassword = compAbstractEvent.extend({
	value : "",
	tag : 'input',

	initial : function(component) {
		this._super(component);
		this.value = component.value;
		this.security = component.security || 0;
		this.tag = 'input';
	},

	get_Html : function() {
		var args = {
			'type' : "password"
		};
		args.value = this.initialVal();
		return this.getBuildHtml(args, true, true);
	},

	initialVal : function() {
		return this.value;
	},

	checkValid : function() {
		this._super();
		if ((this.security !== 0) && !this.getGUIComp().prop("disabled")) {
			var msg_text, inputVal, lowerreg = /^(?=.*[a-z]).+$/, upperreg = /^(?=.*[A-Z]).+$/, noalphareg = /^(?=.*[0-9_\W]).+$/;
			inputVal = this.getGUIComp().val();
			if (inputVal.length < 6) {
				msg_text = Singleton().getTranslate("Password too short!");
				throw new LucteriosException(MINOR, msg_text);
			}
			if (!lowerreg.test(inputVal) || !upperreg.test(inputVal) || !noalphareg.test(inputVal)) {
				msg_text = Singleton().getTranslate("Password too simple!");
				throw new LucteriosException(MINOR, msg_text);
			}
		}
		return;
	},

	addAction : function() {
		this.addActionEx(0);
	}
});

var compDate = compAbstractEvent.extend({
	value : "",
	tag : 'input',

	initial : function(component) {
		this._super(component);
		if (this.is_null === false) {
			this.value = component.value || '';
		}
		if (this.value === '') {
			var today = new Date();
			this.value = "{0}-{1}-{2}".format(today.getFullYear(), (today.getMonth() + 1).toString().lpad('0', 2), today.getDate().toString().lpad(
					'0', 2));
		}
		this.tag = 'input';
	},

	get_Html : function() {
		var args = {
			'type' : "text",
			'cssclass' : "datepicker"
		}, date_nums = this.initialVal().split('-');
		args.value = "{0}/{1}/{2}".format(date_nums[2], date_nums[1], date_nums[0]);
		if (this.needed === false) {
			args.cssclass += ' lctdateneeded';
		} else {
			args.cssclass += ' lctdate';
		}
		return this.addnullcheck() + this.getBuildHtml(args, false, true);
	},

	getValue : function() {
		var date_nums;
		if (this.is_return_null() === true) {
			return NULL_VALUE;
		}
		date_nums = this.getGUIComp().val().split('/');
		return "{0}-{1}-{2}".format(date_nums[2], date_nums[1], date_nums[0]);
	},

	setValue : function(jsonvalue) {
		this.initial(jsonvalue);
		var date_nums = this.initialVal().replace(/\//g, '-').split('-');
		this.getGUIComp().val("{0}/{1}/{2}".format(date_nums[2], date_nums[1], date_nums[0]));
	},

	initialVal : function() {
		return this.value;
	},

	addAction : function() {
		this.addActionEx(0);
	}
});

var compTime = compAbstractEvent.extend({
	value : "",
	tag : 'input',

	initial : function(component) {
		this._super(component);
		if (this.is_null === false) {
			this.value = component.value;
		}
		if (this.value === '') {
			var today = new Date();
			this.value = "{0}:{1}".format(today.getHours().toString().lpad('0', 2), today.getMinutes().toString().lpad('0', 2));
		}
		this.tag = 'input';
	},

	getValue : function() {
		if (this.is_return_null() === true) {
			return NULL_VALUE;
		}
		return this._super();
	},

	get_Html : function() {
		var args = {
			'type' : "text",
			'class' : "timespinner"
		};
		args.value = this.initialVal();
		return this.addnullcheck() + this.getBuildHtml(args, true, true);
	},

	setEnabled : function(isEnabled) {
		if (isEnabled === true) {
			this.getGUIComp().timespinner("enable");
		} else {
			this.getGUIComp().timespinner("disable");
		}
		if (this.descComp !== null) {
			this.descComp.setEnabled(isEnabled);
		}
	},

	initialVal : function() {
		return this.value;
	},

	addAction : function() {
		this.addActionEx(0);
	}

});

var compDateTime = compAbstractEvent.extend({
	value : "",
	tag : 'input',

	initial : function(component) {
		this._super(component);
		if (this.is_null === false) {
			this.value = component.value;
		}
		if (this.value === '') {
			var today = new Date();
			this.value = "{0}-{1}-{2} {3}:{4}".format(today.getFullYear(), (today.getMonth() + 1).toString().lpad('0', 2), today.getDate().toString()
					.lpad('0', 2), today.getHours().toString().lpad('0', 2), today.getMinutes().toString().lpad('0', 2));
		}
		this.tag = 'input';
	},

	getGUICompTime : function() {
		return $("#" + this.owner.getId()).find("{0}[name='{1}']:eq(1)".format(this.tag, this.name));
	},

	get_Html : function() {
		var date_time = this.initialVal().split(' '), date_nums = date_time[0].split('-'), args_dt = {
			'type' : "text",
			'cssclass' : "datepicker lctdate"
		}, args_tm = {
			'type' : "text",
			'cssclass' : "timespinner lcttime"
		};
		args_dt.value = "{0}/{1}/{2}".format(date_nums[2], date_nums[1], date_nums[0]);
		args_tm.value = date_time[1];
		return this.addnullcheck() + this.getBuildHtml(args_dt, false, true) + this.getBuildHtml(args_tm, false, true);
	},

	initialVal : function() {
		return this.value;
	},

	getValue : function() {
		var date_nums;
		if (this.is_return_null() === true) {
			return NULL_VALUE;
		}
		date_nums = this.getGUIComp().val().split('/');
		return "{0}-{1}-{2} {3}".format(date_nums[2], date_nums[1], date_nums[0], this.getGUICompTime().val());
	},

	setEnabled : function(isEnabled) {
		this.getGUIComp().prop("disabled", !isEnabled);
		if (isEnabled === true) {
			this.getGUICompTime().timespinner("enable");
		} else {
			this.getGUICompTime().timespinner("disable");
		}
		if (this.descComp !== null) {
			this.descComp.setEnabled(isEnabled);
		}
	},

	setValue : function(jsonvalue) {
		this.initial(jsonvalue);
		var date_time = this.initialVal().split(' '), date_nums = date_time[0].split('-');
		this.getGUIComp().val("{0}/{1}/{2}".format(date_nums[2], date_nums[1], date_nums[0]));
		this.getGUICompTime().val(date_time[1]);
	},

	addAction : function() {
		var act_function = this.get_act_function();
		if (act_function !== null) {
			this.getGUIComp().focusout($.proxy(act_function, this));
			this.getGUICompTime().focusout($.proxy(act_function, this));
		}
		this.addActionNull(act_function);
	}

});

var compSelectCase = Class.extend({
	id : 0,
	label : "",
	checked : false,

	initial : function(component) {
		this.id = component[0].toString();
		this.label = component[1];
		if (this.label === null) {
			this.label = '---';
		}
	},

	get_Html : function(value) {
		var html = '<option value="' + this.id + '"';
		if (((value !== null) && (value.toString() === this.id)) || ((value === null) && this.checked)) {
			html += ' selected';
		}
		html += '>' + this.label + '</option>';
		return html;
	}
});

var compSelect = compAbstractEvent.extend({
	cases : null,
	value : "",
	tag : 'select',
	args : {
		'cssclass' : ''
	},

	initial : function(component) {
		this._super(component);

		// traitement des HEADER
		this.cases = [];
		var iChild, cas;
		for (iChild = 0; iChild < component['case'].length; iChild++) {
			cas = new compSelectCase();
			cas.initial(component['case'][iChild]);
			this.cases[this.cases.length] = cas;
		}
		this.value = component.value;
		if (this.value === undefined) {
			this.value = '';
		}
		this.tag = 'select';

		this.after_initial(component);
	},

	after_initial : function(component) {
		unusedVariables(component);
		if ((this.value === '') && (this.cases.length > 0)) {
			this.value = this.cases[0].id;
		}
	},

	getOptionVal : function() {
		var html = '', iHead;
		for (iHead = 0; iHead < this.cases.length; iHead++) {
			html += this.cases[iHead].get_Html(this.value);
		}
		return html;
	},

	get_Html : function() {
		var html = this.getBuildHtml(this.args, true, false);
		html += this.getOptionVal();
		html += '</{0}>'.format(this.tag);
		return html;
	},

	setValue : function(jsonvalue) {
		this.initial(jsonvalue);
		this.getGUIComp().html(this.getOptionVal());
	},

	initialVal : function() {
		return this.value;
	},

	addAction : function() {
		this.addActionEx(2);
	}
});

var compCheckList = compSelect.extend({

	after_initial : function(component) {
		var iHead;
		this.simple = parseInt(component.simple, 10) || 0;
		this.args = {
			'cssclass' : "checklist"
		};
		if (!Array.isArray(this.value)) {
			this.value = [];
		}
		this.args.multiple = 'multiple';
		if (this.simple === 2) {
			this.tag = 'span';
			this.args.cssclass = 'multiselect';
		}
		for (iHead = 0; iHead < this.cases.length; iHead++) {
			this.cases[iHead].checked = (this.value.indexOf(this.cases[iHead].id) !== -1);
		}
	},

	initialVal : function() {
		if (this.value.length === 0) {
			return '';
		}
		return this.value.join(';');
	},

	fillValue : function(params) {
		var res = this.getValue();
		if (res !== this.initialVal()) {
			params.put(this.name, res);
		}
	},

	getValue : function() {
		var res, iHead;
		if (this.simple === 2) {
			res = [];
			for (iHead = 0; iHead < this.cases.length; iHead++) {
				if (this.cases[iHead].checked) {
					res.push(this.cases[iHead].id);
				}
			}
		} else {
			res = this.getGUIComp().val();
		}
		if (res === null) {
			return "";
		}
		return res.join(';');
	},

	getOptionVal : function() {
		var html = '', iHead;
		if (this.simple !== 2) {
			for (iHead = 0; iHead < this.cases.length; iHead++) {
				html += this.cases[iHead].get_Html(null);
			}
		} else {
			html += '<lct-checklist>';
			html += '<select name="{0}_available" multiple = "multiple">'.format(this.name);
			for (iHead = 0; iHead < this.cases.length; iHead++) {
				if (!this.cases[iHead].checked) {
					html += this.cases[iHead].get_Html(0);
				}
			}
			html += '</select>';
			html += '<div>';
			html += '<button class="addall" name="{0}_addall"><span class="fa fa-plus-square"/></button>'.format(this.name);
			html += '<button class="add" name="{0}_add"><span class="fa fa-plus-square-o"/></button>'.format(this.name);
			html += '<button class="del" name="{0}_del"><span class="fa fa-minus-square-o"/></button>'.format(this.name);
			html += '<button class="delall" name="{0}_delall"><span class="fa fa-minus-square"/></button>'.format(this.name);
			html += '</div>';
			html += '<select name="{0}_chosen" multiple = "multiple">'.format(this.name);
			for (iHead = 0; iHead < this.cases.length; iHead++) {
				if (this.cases[iHead].checked) {
					html += this.cases[iHead].get_Html(0);
				}
			}
			html += '</select>';
			html += '</lct-checklist>';
		}
		return html;
	},

	addAction : function() {
		if (this.simple === 1) {
			this.addActionEx(2);
		} else if (this.simple === 2) {
			this.getGUIComp().find("button[name='{0}_addall']:eq(0)".format(this.name)).click($.proxy(this.addallbtn, this));
			this.getGUIComp().find("button[name='{0}_add']:eq(0)".format(this.name)).click($.proxy(this.addbtn, this));
			this.getGUIComp().find("button[name='{0}_del']:eq(0)".format(this.name)).click($.proxy(this.delbtn, this));
			this.getGUIComp().find("button[name='{0}_delall']:eq(0)".format(this.name)).click($.proxy(this.delallbtn, this));
		} else {
			this.addActionEx(0);
		}
	},

	clickafterbtn : function() {
		var act_function = this.get_act_function();
		this.getGUIComp().html(this.getOptionVal());
		this.addAction();
		if (act_function !== null) {
			$.proxy(act_function, this)();
		}
	},

	addallbtn : function() {
		var iHead;
		for (iHead = 0; iHead < this.cases.length; iHead++) {
			this.cases[iHead].checked = true;
		}
		this.clickafterbtn();
	},

	addbtn : function() {
		var iHead, val_available = this.getGUIComp().find("select[name='{0}_available']:eq(0)".format(this.name)).val();
		if (val_available !== null) {
			for (iHead = 0; iHead < this.cases.length; iHead++) {
				if (val_available.indexOf(this.cases[iHead].id) !== -1) {
					this.cases[iHead].checked = true;
				}
			}
		}
		this.clickafterbtn();
	},

	delbtn : function() {
		var iHead, val_chosen = this.getGUIComp().find("select[name='{0}_chosen']:eq(0)".format(this.name)).val();
		if (val_chosen !== null) {
			for (iHead = 0; iHead < this.cases.length; iHead++) {
				if (val_chosen.indexOf(this.cases[iHead].id) !== -1) {
					this.cases[iHead].checked = false;
				}
			}
		}
		this.clickafterbtn();
	},

	delallbtn : function() {
		var iHead;
		for (iHead = 0; iHead < this.cases.length; iHead++) {
			this.cases[iHead].checked = false;
		}
		this.clickafterbtn();
	}

});

var compUpload = compGeneric
		.extend({
			filter : "",
			compress : false,
			httpFile : false,
			maxsize : 0,

			content : null,
			content_isloading : true,

			initial : function(component) {
				this._super(component);
				this.filter = '';
				var filters = component.filter;
				this.filter = filters.join(',');
				this.compress = component.compress;
				this.httpFile = component.http_file;
				this.maxsize = component.maxsize || 0;
				this.tag = 'input';
			},

			get_Html : function() {
				var args = {
					'type' : "file",
					'accept' : this.filter
				};
				return this.getBuildHtml(args, true, true);
			},

			getEncodeFile : function(fileToSend) {
				var size, reader;
				if (fileToSend.size > this.maxsize) {
					size = this.maxsize / (1024 * 1024);
					throw new LucteriosException(IMPORTANT, Singleton().getTranslate("Upload impossible<br/>The file must be less than {0}Mo ")
							.format(size));
				}
				if (this.httpFile) {
					this.content = fileToSend;
					this.content_isloading = false;
				} else {
					reader = new FileReader();
					if (typeof reader.readAsBinaryString === "function") {
						reader.onload = $.proxy(function(readerEvt) {
							var binaryString = readerEvt.target.result;
							this.content = fileToSend.name + ";" + btoa(binaryString);
							this.content_isloading = false;
						}, this);
						reader.readAsBinaryString(fileToSend);
					} else {
						reader.addEventListener("loadend", function() {
							var binary = "", bytes, length, iLetter;
							bytes = new Uint8Array(reader.result);
							length = bytes.byteLength;
							for (iLetter = 0; iLetter < length; iLetter++) {
								binary += String.fromCharCode(bytes[iLetter]);
							}
							this.content = fileToSend.name + ";" + btoa(binary);
						});
						reader.readAsArrayBuffer(fileToSend);
					}
				}
			},

			getFileContentBase64 : function() {
				this.content = null;
				this.content_isloading = true;
				if (this.compress) {
					zip.useWebWorkers = true;
					zip.workerScriptsPath = "lib/";
					var current_upcomp = this, file_to_zip = this.getValue();
					zip.createWriter(new zip.BlobWriter("application/zip"), function(zipWriter) {
						zipWriter.add(file_to_zip.name, new zip.BlobReader(file_to_zip), function() {
							zipWriter.close($.proxy(current_upcomp.getEncodeFile, current_upcomp));
						});
					}, function(message) {
						throw new LucteriosException(GRAVE, "Zip compression:" + message);
					});
				} else {
					this.getEncodeFile(this.getValue());
				}
			},

			addAction : function() {
				var gui_comp = this.getGUIComp();
				gui_comp.change($.proxy(this.getFileContentBase64, this));
			},

			getValue : function() {
				var comp = this.getGUIComp();
				if (comp[0].files.length > 0) {
					return comp[0].files[0];
				}
				return null;
			},

			fillValue : function(params) {
				var file_to_zip = this.getValue(), new_file;
				if (file_to_zip !== null) {
					if (this.content_isloading) {
						throw new LucteriosException(MINOR, Singleton().getTranslate("Loading..."));
					}
					if (this.content !== null) {
						params.put(this.name, this.content);
						if (this.compress) {
							new_file = this.getValue();
							params.put(this.name + "_FILENAME", new_file.name);
						}
					}
				}
			}

		});

var compdownload = compGeneric
		.extend({
			compress : false,
			httpFile : false,
			maxsize : 0,
			file_name : '',
			link_file_name : '',

			initial : function(component) {
				this._super(component);
				this.compress = component.compress;
				this.httpFile = component.http_file;
				this.maxsize = component.maxsize || 0;
				this.file_name = component.value.trim();
				this.link_file_name = component.filename;
				this.needed = 0;
				this.tag = 'button';
			},

			checkValid : function() {
				return;
			},

			get_Html : function() {
				var args = {
					'id' : 'download_{0}_{1}'.format(this.owner.getId(), this.name)
				};
				return "<label>" + this.file_name + "</label>" + this.getBuildHtml(args, false, false) + Singleton().getTranslate("Save as...")
						+ "</button>";
			},

			addAction : function() {
				this.getGUIComp().click($.proxy(this.open_file, this));
			},

			open_file : function() {
				Singleton().Transport().getFileContent(this.link_file_name, $.proxy(this.receive_blob, this));
			},

			receive_blob : function(blob) {
				if (this.compress) {
					zip.useWebWorkers = true;
					zip.workerScriptsPath = "lib/";
					var file_name_to_load = this.file_name;
					zip.createReader(new zip.BlobReader(blob), function(zipReader) {
						zipReader.getEntries(function(entries) {
							entries[0].getData(new zip.BlobWriter("text/plain"), function(data_blob) {
								zipReader.close();
								Singleton().mFileManager.saveBlob(data_blob, file_name_to_load);
							});
						});
					}, function(message) {
						throw new LucteriosException(GRAVE, "Zip decompression:" + message);
					});
				} else {
					Singleton().mFileManager.saveBlob(blob, this.file_name);
				}
			}

		});
