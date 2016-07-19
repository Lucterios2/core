/*global $,LucteriosException,CRITIC,IMPORTANT,GRAVE,MINOR,compGeneric,Class,Singleton,post_log,SELECT_NONE,SELECT_SINGLE,SELECT_MULTI,zip,NULL_VALUE,unusedVariables*/
/*jslint regexp: true */

// image
var compImage = compGeneric.extend({
	height : 0,
	width : 0,
	src : "",
	type : "",

	initial : function(component) {
		this._super(component);
		this.height = component.getAttribute("height");
		this.width = component.getAttribute("width");
		this.src = component.getTextFromXmlNode();
		this.type = component.getCDataOfFirstTag("TYPE");
		if (this.type === '') {
			this.type = component.getXMLAttributStr("type", '');
		}
		this.needed = 0;
		this.tag = 'img';
	},

	checkValid : function() {
		return;
	},

	getHtml : function() {
		var src_img = this.src;
		if (this.type === '') {
			src_img = Singleton().Transport().getIconUrl(
					this.src + "?val=" + Math.floor(Math.random() * 1000));
		} else {
			if (this.src.substring(0, 10) === 'data:image') {
				src_img = this.src;
			} else {
				src_img = 'data:image/{0};base64,{1}'.format(this.type,
						this.src);
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

		this.label = component.getTextFromXmlNode()
				.convertLuctoriosFormatToHtml();
		this.tag = 'span';
	},

	checkValid : function() {
		return;
	},

	getHtml : function() {
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

	getHtml : function() {
		var args = {
			'type' : "text",
			'style' : "width:20px"
		};
		args.value = '';
		return "{0} {1} {2} = {3}".format(this.num1, this.operation_txt, this
				.getBuildHtml(args, false, true), this.total);
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
var compAbstractEvent = compGeneric
		.extend({
			action : null,
			java_script_content : null,

			initial : function(component) {
				this._super(component);
				var acts = component.getElementsByTagName("ACTIONS"), act;
				if (acts.length > 0) {
					act = acts[0].getElementsByTagName("ACTION");
					if (act.length > 0) {
						this.action = Singleton().CreateAction();
						this.action.initialize(this.owner, Singleton()
								.Factory(), act[0]);
						this.action.setCheckNull(false);
					}
				}
				this.java_script_content = decodeURIComponent(component
						.getCDataOfFirstTag('JavaScript').replace(/\+/g, " "));
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
							adder = new Function("current", "parent",
									this.java_script_content); /* jshint -W054 */
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
						adder = new Function("current", "parent",
								this.java_script_content); /* jshint -W054 */
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
					nullcheck = $("#" + this.owner.getId()).find(
							"input[name='nullcheck_{0}']:eq(0)"
									.format(this.name));
					nullcheck.change($.proxy(function() {
						if (act_function !== null) {
							$.proxy(act_function, this)();
						}
						this.setEnabled(!nullcheck[0].checked);
					}, this));
					this.setEnabled(!this.is_null);
				}
			},

			addnullcheck : function() {
				var res = '', valcheck = '';
				if (this.needed === false) {
					if (this.is_null === true) {
						valcheck = 'checked = "checked"';
					}
					res = '<input class="class_checknull" type="checkbox" name="nullcheck_{0}" {1}/>'
							.format(this.name, valcheck);
				}
				return res;
			},

			is_return_null : function() {
				var res = false, nullcheck;
				if (this.needed === false) {
					nullcheck = $("#" + this.owner.getId()).find(
							"input[name='nullcheck_{0}']:eq(0)"
									.format(this.name));
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

	initial : function(component) {
		this._super(component);
		this.clickName = component.getAttribute("clickname");
		this.clickValue = component.getAttribute("clickvalue");
		this.isMini = (component.getXMLAttributInt("isMini", 0) === 1);
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

	getHtml : function() {
		if (this.action !== null) {
			var arg = {}, title, btn_icon;
			this.btnaction = this.action;
			this.action = this;
			if (this.isMini) {
				arg.style = 'width:30px;padding: 0px;';
			}
			if (!this.isMini || (this.btnaction.getIcon() === '')) {
				title = this.btnaction.getTitle();
			} else {
				title = '';
			}
			if (this.btnaction.getIcon() !== '') {
				btn_icon = Singleton().Transport().getIconUrl(
						this.btnaction.getIcon());
				title = '<img src="{0}" style="max-width:32px"/>'
						.format(btn_icon)
						+ title;
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
	},

	fillValue : function(params) {
		if (this.hasBeenClicked) {
			params.put(this.clickName, this.clickValue);
		}
	}

});

// case à cocher
var compCheck = compAbstractEvent.extend({
	// generiques
	checked : 0,

	initial : function(component) {
		this._super(component);

		var val = component.getTextFromXmlNode();
		this.checked = (val === '1') || (val === 'o');
		this.tag = 'input';
	},

	getHtml : function() {
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

	setValue : function(xmlValue) {
		this.initial(xmlValue.parseXML());
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

	initial : function(component) {
		this._super(component);
		this.label = component.getTextFromXmlNode()
				.convertLuctoriosFormatToHtml();
		this.link = component.getCDataOfFirstTag("LINK");
		this.needed = 0;
		this.tag = 'a';
	},

	checkValid : function() {
		return;
	},

	getHtml : function() {
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

	initial : function(component) {
		var regex;
		this._super(component);
		this.value = component.getTextFromXmlNode();
		this.size = component.getXMLAttributInt("size", -1);
		regex = component.getCDataOfFirstTag("REG_EXPR");
		if (regex !== '') {
			this.mask = new RegExp(regex, 'i');
		}
		this.tag = 'input';
	},

	getHtml : function() {
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
			this.getGUIComp().keyup(
					$.proxy(
							function() {
								var inputVal = this.getGUIComp().val();
								if (((this.mask !== null) && !this.mask
										.test(inputVal))
										|| ((this.size !== -1) && (inputVal
												.trim().length > this.size))) {
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

var compFloat = compAbstractEvent
		.extend({
			value : "",
			min : 0,
			max : 1000,
			prec : 1,

			initial : function(component) {
				this._super(component);
				var text_value = '', nb_dec = component.getXMLAttributInt(
						'prec', 0), dec_i;
				if (this.is_null === false) {
					text_value = component.getTextFromXmlNode();
				}
				if (text_value === '') {
					text_value = '0';
				}
				this.value = parseFloat(text_value);
				this.min = component.getXMLAttributFloat('min', 0.0);
				this.max = component.getXMLAttributFloat('max', 1000.0);
				this.prec = 1;
				for (dec_i = 0; dec_i < nb_dec; dec_i++) {
					this.prec = this.prec / 10;
				}
				this.tag = 'input';
			},

			getHtml : function() {
				var args = {
					'type' : "text"
				};
				args.value = this.initialVal();
				return this.addnullcheck()
						+ this.getBuildHtml(args, true, true);
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
				return this.value;
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

var editorHypertext = Class
		.extend({
			name : '',
			with_hypertext : false,
			sub_menus : [],
			init : function(aOwnerId, aName, aWith_hypertext, aSub_menu_xml) {
				var isub_menu, sub_menu, sub_menu_name, sub_menu_value;
				this.ownerId = aOwnerId;
				this.name = aName;
				this.with_hypertext = aWith_hypertext;
				this.sub_menus = [];
				for (isub_menu = 0; isub_menu < aSub_menu_xml.length; isub_menu++) {
					sub_menu = aSub_menu_xml[isub_menu];
					sub_menu_name = sub_menu.getCDataOfFirstTag("NAME");
					sub_menu_value = sub_menu.getCDataOfFirstTag("VALUE");
					this.sub_menus[this.sub_menus.length] = [ sub_menu_name,
							sub_menu_value ];
				}
			},
			getGUIComp : function() {
				return $("#" + this.ownerId).find(
						"textarea[name='{0}']:eq(0)".format(this.name));
			},
			getHtml : function(attribut, value) {
				var html = "", imenu, sub_menu;
				html += '<ul id="menu_{0}" class="contextMenu">'
						.format(this.name);
				for (imenu = 0; imenu < this.sub_menus.length; imenu++) {
					sub_menu = this.sub_menus[imenu];
					html += '<li><a href="#menu_{0}">{1}</a></li>'.format(
							imenu, sub_menu[0]);
				}
				html += '</ul>';
				if (this.with_hypertext === 1) {
					html += '<div class="ui-widget-header">';
					html += '<img id="bold_{0}" src="images/bold.png" class="memobtn">'
							.format(this.name);
					html += '<img id="italic_{0}" src="images/italic.png" class="memobtn">'
							.format(this.name);
					html += '<img id="underline_{0}" src="images/underline.png" class="memobtn">'
							.format(this.name);
					html += '<img id="black_{0}" src="images/black.png" class="memobtn">'
							.format(this.name);
					html += '<img id="blue_{0}" src="images/blue.png" class="memobtn">'
							.format(this.name);
					html += '<img id="red_{0}" src="images/red.png" class="memobtn">'
							.format(this.name);
					html += '<img id="green_{0}" src="images/green.png" class="memobtn">'
							.format(this.name);
					html += '</div>';
				}
				html += '<textarea ' + attribut + '>' + value + '</textarea>';
				return html;
			},
			addEditorAction : function() {
				var menu_name = "menu_{0}".format(this.name), area_name = "textarea[name='{0}']"
						.format(this.name), self = this;
				if (this.sub_menus.length > 0) {
					$(area_name)
							.contextMenu(
									{
										menu : menu_name
									},
									function(action, el, pos) {
										unusedVariables(el);
										unusedVariables(pos);
										var cursorPos, val_area, variable_text, textBefore, textAfter, variable_id;
										variable_id = parseInt(action
												.substring(5, action.length),
												10);
										variable_text = "#"
												+ self.sub_menus[variable_id][1];
										cursorPos = self.getGUIComp().prop(
												'selectionStart');
										val_area = self.getGUIComp().val();
										textBefore = val_area.substring(0,
												cursorPos);
										textAfter = val_area.substring(
												cursorPos, val_area.length);
										self.getGUIComp().val(
												textBefore + variable_text
														+ textAfter);
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
				this.getGUIComp().val(
						"{0}{[{1}{2}]}{3}{[/{1}]}{4}".format(textBefore,
								tagname, extra, select_val, textAfter));
			}

		});

var compMemo = compAbstractEvent.extend({
	value : "",

	initial : function(component) {
		this._super(component);
		this.value = component.getTextFromXmlNode().replace(/\{\[newline\]\}/g,
				"\n");
		this.editor = new editorHypertext(this.owner.getId(), this.name,
				component.getXMLAttributInt('with_hypertext', 0), component
						.getElementsByTagName("SUBMENU"));
		this.tag = 'textarea';
	},

	getHtml : function() {
		return this.editor.getHtml(this.getAttribHtml({}, true), this
				.initialVal());
	},

	initialVal : function() {
		return this.value;
	},

	fillValue : function(params) {
		var val = this.getValue();
		params.put(this.name, val.replace(/\n/g, '{[newline]}'));
	},

	addAction : function() {
		this.addActionEx(0);
		this.editor.addEditorAction();
	}
});

var compXML = compAbstractEvent.extend({
	value : "",

	initial : function(component) {
		this._super(component);
		this.value = component.getTextFromXmlNode();
		this.editor = new editorHypertext(this.owner.getId(), this.name, 1,
				component.getElementsByTagName("SUBMENU"));
		this.tag = 'textarea';
	},

	getHtml : function() {
		return this.editor.getHtml(this.getAttribHtml({}, true), this
				.initialVal());
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

var compPassword = compAbstractEvent
		.extend({
			value : "",

			initial : function(component) {
				this._super(component);
				this.value = component.getTextFromXmlNode();
				this.security = component.getXMLAttributInt('security', 0);
				this.tag = 'input';
			},

			getHtml : function() {
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
				if ((this.security !== 0)
						&& !this.getGUIComp().prop("disabled")) {
					var msg_text, inputVal, lowerreg = /^(?=.*[a-z]).+$/, upperreg = /^(?=.*[A-Z]).+$/, noalphareg = /^(?=.*[0-9_\W]).+$/;
					inputVal = this.getGUIComp().val();
					if (inputVal.length < 6) {
						msg_text = Singleton().getTranslate(
								"Password too short!");
						throw new LucteriosException(MINOR, msg_text);
					}
					if (!lowerreg.test(inputVal) || !upperreg.test(inputVal)
							|| !noalphareg.test(inputVal)) {
						msg_text = Singleton().getTranslate(
								"Password too simple!");
						throw new LucteriosException(MINOR, msg_text);
					}
				}
				return;
			},

			addAction : function() {
				this.addActionEx(0);
			}
		});

var compDate = compAbstractEvent
		.extend({
			value : "",

			initial : function(component) {
				this._super(component);
				if (this.is_null === false) {
					this.value = component.getTextFromXmlNode();
				}
				if (this.value === '') {
					var today = new Date();
					this.value = "{0}-{1}-{2}".format(today.getFullYear(),
							(today.getMonth() + 1).toString().lpad('0', 2),
							today.getDate().toString().lpad('0', 2));
				}
				this.tag = 'input';
			},

			getHtml : function() {
				var args = {
					'type' : "text",
					'class' : "datepicker",
					'style' : "width:80%;margin:5px 0px 5px 5px;"
				}, date_nums = this.initialVal().split('-');
				args.value = "{0}/{1}/{2}".format(date_nums[2], date_nums[1],
						date_nums[0]);
				if (this.needed === false) {
					args.style = "width:70%;margin:5px 0px 5px 0px;";
				}
				return this.addnullcheck()
						+ this.getBuildHtml(args, false, true);
			},

			getValue : function() {
				var date_nums;
				if (this.is_return_null() === true) {
					return NULL_VALUE;
				}
				date_nums = this.getGUIComp().val().split('/');
				return "{0}-{1}-{2}".format(date_nums[2], date_nums[1],
						date_nums[0]);
			},

			setValue : function(xmlValue) {
				this.initial(xmlValue.parseXML());
				var date_nums = this.initialVal().replace(/\//g, '-')
						.split('-');
				this.getGUIComp().val(
						"{0}/{1}/{2}".format(date_nums[2], date_nums[1],
								date_nums[0]));
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

	initial : function(component) {
		this._super(component);
		if (this.is_null === false) {
			this.value = component.getTextFromXmlNode();
		}
		if (this.value === '') {
			var today = new Date();
			this.value = "{0}:{1}".format(today.getHours().toString().lpad('0',
					2), today.getMinutes().toString().lpad('0', 2));
		}
		this.tag = 'input';
	},

	getValue : function() {
		if (this.is_return_null() === true) {
			return NULL_VALUE;
		}
		return this._super();
	},

	getHtml : function() {
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
	},

	initialVal : function() {
		return this.value;
	},

	addAction : function() {
		this.addActionEx(0);
	}

});

var compDateTime = compAbstractEvent
		.extend({

			value : "",

			initial : function(component) {
				this._super(component);
				if (this.is_null === false) {
					this.value = component.getTextFromXmlNode();
				}
				if (this.value === '') {
					var today = new Date();
					this.value = "{0}-{1}-{2} {3}:{4}".format(today
							.getFullYear(), (today.getMonth() + 1).toString()
							.lpad('0', 2), today.getDate().toString().lpad('0',
							2), today.getHours().toString().lpad('0', 2), today
							.getMinutes().toString().lpad('0', 2));
				}
				this.tag = 'input';
			},

			getGUICompTime : function() {
				return $("#" + this.owner.getId()).find(
						"{0}[name='{1}']:eq(1)".format(this.tag, this.name));
			},

			getHtml : function() {
				var date_time = this.initialVal().split(' '), date_nums = date_time[0]
						.split('-'), args_dt = {
					'type' : "text",
					'class' : "datepicker",
					'style' : "width:40%;margin:5px;"
				}, args_tm = {
					'type' : "text",
					'class' : "timespinner",
					'style' : "width:30%;margin:5px;"
				};
				args_dt.value = "{0}/{1}/{2}".format(date_nums[2],
						date_nums[1], date_nums[0]);
				args_tm.value = date_time[1];
				return this.addnullcheck()
						+ this.getBuildHtml(args_dt, false, true)
						+ this.getBuildHtml(args_tm, false, true);
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
				return "{0}-{1}-{2} {3}".format(date_nums[2], date_nums[1],
						date_nums[0], this.getGUICompTime().val());
			},

			setEnabled : function(isEnabled) {
				this.getGUIComp().prop("disabled", !isEnabled);
				if (isEnabled === true) {
					this.getGUICompTime().timespinner("enable");
				} else {
					this.getGUICompTime().timespinner("disable");
				}
			},

			setValue : function(xmlValue) {
				this.initial(xmlValue.parseXML());
				var date_time = this.initialVal().split(' '), date_nums = date_time[0]
						.split('-');
				this.getGUIComp().val(
						"{0}/{1}/{2}".format(date_nums[2], date_nums[1],
								date_nums[0]));
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
	checked : null,

	initial : function(component) {
		this.id = component.getAttribute("id");
		this.label = component.getTextFromXmlNode();
		this.checked = component.getAttribute('checked');
	},

	getHtml : function(value) {
		var html = '<option value="' + this.id + '"';
		if (((value !== null) && (value === this.id))
				|| ((value === null) && (this.checked === '1'))) {
			html += ' selected';
		}
		html += '>' + this.label + '</option>';
		return html;
	}
});

var compSelect = compAbstractEvent.extend({
	cases : null,
	value : "",
	args : {},

	initial : function(component) {
		this._super(component);

		// traitement des HEADER
		this.cases = [];
		var cass = component.getElementsByTagName("CASE"), iChild, cas;
		for (iChild = 0; iChild < cass.length; iChild++) {
			cas = new compSelectCase();
			cas.initial(cass[iChild]);
			this.cases[this.cases.length] = cas;
		}
		if ((component.firstChild !== null)
				&& (component.firstChild.nodeValue !== null)) {
			this.value = component.firstChild.nodeValue.trim();
		} else {
			this.value = '';
		}
		this.tag = 'select';
	},

	getOptionVal : function() {
		var html = '', iHead;
		for (iHead = 0; iHead < this.cases.length; iHead++) {
			html += this.cases[iHead].getHtml(this.value);
		}
		return html;
	},

	getHtml : function() {
		var html = this.getBuildHtml(this.args, true, false);
		html += this.getOptionVal();
		html += '</select>';
		return html;
	},

	setValue : function(xmlValue) {
		this.initial(xmlValue.parseXML());
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

	initial : function(component) {
		this._super(component);
		this.simple = (component.getXMLAttributInt('simple', 0) === 1);
		this.args = {
			'class' : "checklist"
		};
		this.args.multiple = 'multiple';
		this.value = [];
	},

	getOptionVal : function() {
		var html = '', iHead;
		for (iHead = 0; iHead < this.cases.length; iHead++) {
			html += this.cases[iHead].getHtml(null);
			if (this.cases[iHead].checked === '1') {
				this.value.push(this.cases[iHead].id);
			}
		}
		return html;
	},

	addAction : function() {
		if (this.simple) {
			this.addActionEx(2);
		} else {
			this.addActionEx(0);
		}
	},

	initialVal : function() {
		if (this.value.length === 0) {
			return null;
		}
		return this.value.join(';');
	},

	fillValue : function(params) {
		var res = this.getGUIComp().val();
		if ((res !== null) && (res !== this.value)) {
			params.put(this.name, res.join(';'));
		}
	},

	getValue : function() {
		if (this.getGUIComp().val() === null) {
			return "";
		}
		var res = this.getGUIComp().val();
		return res.join(';');
	}

});

var compUpload = compGeneric.extend({
	filter : "",
	compress : false,
	httpFile : false,
	maxsize : 0,

	content : null,
	content_isloading : true,

	initial : function(component) {
		this._super(component);
		this.filter = '';
		var filters = component.getElementsByTagName("FILTER"), msg_text, iChild, textreader = new FileReader();
		if (typeof textreader.readAsBinaryString !== "function") { 
			msg_text = Singleton().getTranslate("This Web browser don't support this feature!\nUse Firefox, Chrome, Safari or Edge.");
			throw new LucteriosException(IMPORTANT, msg_text);
		}		
		for (iChild = 0; iChild < filters.length; iChild++) {
			if (this.filter !== '') {
				this.filter += ',';
			}
			this.filter += filters[iChild].getTextFromXmlNode();
		}
		this.compress = (component.getXMLAttributInt("Compress", 0) === 1);
		this.httpFile = (component.getXMLAttributInt("HttpFile", 0) === 1);
		this.maxsize = component.getXMLAttributInt("maxsize", 0);
		this.tag = 'input';
	},

	getHtml : function() {
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
			throw new LucteriosException(IMPORTANT, Singleton().getTranslate(
					"Upload impossible<br/>The file must be less than {0}Mo ")
					.format(size));
		}
		if (this.httpFile) {
			this.content = fileToSend;
			this.content_isloading = false;
		} else {
			reader = new FileReader();
			reader.onload = $.proxy(function(readerEvt) {
				var binaryString = readerEvt.target.result;
				this.content = fileToSend.name + ";" + btoa(binaryString);
				this.content_isloading = false;
			}, this);
			reader.readAsBinaryString(fileToSend);
		}
	},

	getFileContentBase64 : function() {
		this.content = null;
		this.content_isloading = true;
		if (this.compress) {
			zip.useWebWorkers = true;
			zip.workerScriptsPath = "lib/";
			var current_upcomp = this, file_to_zip = this.getValue();
			zip.createWriter(new zip.BlobWriter("application/zip"), function(
					zipWriter) {
				zipWriter.add(file_to_zip.name,
						new zip.BlobReader(file_to_zip), function() {
							zipWriter.close($.proxy(
									current_upcomp.getEncodeFile,
									current_upcomp));
						});
			}, function(message) {
				throw new LucteriosException(GRAVE, "Zip compression:"
						+ message);
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
				throw new LucteriosException(MINOR, Singleton().getTranslate(
						"Loading..."));
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

var compdownload = compGeneric.extend({
	compress : false,
	httpFile : false,
	maxsize : 0,
	file_name : '',
	link_file_name : '',

	initial : function(component) {
		this._super(component);
		this.compress = (component.getXMLAttributInt("Compress", 0) === 1);
		this.httpFile = (component.getXMLAttributInt("HttpFile", 0) === 1);
		this.maxsize = component.getXMLAttributInt("maxsize", 0);
		this.file_name = component.getTextFromXmlNode().trim();
		this.link_file_name = component.getCDataOfFirstTag("FILENAME");
		this.needed = 0;
		this.tag = 'button';
	},

	checkValid : function() {
		return;
	},

	getHtml : function() {
		var args = {
			'id' : 'download_{0}_{1}'.format(this.owner.getId(), this.name)
		};
		return "<label>" + this.file_name + "</label>"
				+ this.getBuildHtml(args, false, false)
				+ Singleton().getTranslate("Save as...") + "</button>";
	},

	addAction : function() {
		var gui_btn = $('#download_{0}_{1}'.format(this.owner.getId(),
				this.name));
		gui_btn.click($.proxy(this.open_file, this));
	},

	open_file : function() {
		Singleton().Transport().getFileContent(this.link_file_name,
				$.proxy(this.receive_blob, this));
	},

	receive_blob : function(blob) {
		if (this.compress) {
			zip.useWebWorkers = true;
			zip.workerScriptsPath = "lib/";
			var file_name_to_load = this.file_name;
			zip.createReader(new zip.BlobReader(blob), function(zipReader) {
				zipReader.getEntries(function(entries) {
					entries[0].getData(new zip.BlobWriter("text/plain"),
							function(data_blob) {
								zipReader.close();
								Singleton().mFileManager.saveBlob(data_blob,
										file_name_to_load);
							});
				});
			}, function(message) {
				throw new LucteriosException(GRAVE, "Zip decompression:"
						+ message);
			});
		} else {
			Singleton().mFileManager.saveBlob(blob, this.file_name);
		}
	}

});
