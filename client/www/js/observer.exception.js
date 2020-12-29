/*global $,ObserverAbstract,Singleton, compBasic, GUIManage, createTable, createTab, unusedVariables, FAILURE, CRITIC, GRAVE, IMPORTANT, MINOR */
/*global G_Multi_Server, config_servers, ActionInt */

var ObserverException = ObserverAbstract
		.extend({
			message : "",
			code : 0,
			mode : 0,
			debug_info : "",
			type : "",
			user_info : "",
			stack_text : "",

			getObserverName : function() {
				return "core.exception";
			},

			setContent : function(aJSON) {
				this._super(aJSON);
				var json_error = this.mJSON.exception;
				this.message = json_error.message;
				this.code = parseInt("0" + json_error.code, 10);
				this.debug_info = json_error.debug;
				this.type = json_error.type;

				this.requette = json_error.requette || '';
				if (this.requette === '') {
					this.requette = Singleton().Factory().m_Parameters;
				}
				if (this.requette === '*') {
					this.requette = '';
				}
				this.reponse = json_error.response || '';
				this.stack_text = this.get_stack_text();
			},

			get_info : function(aInfo) {
				var res = aInfo.replace(/\n/g, '***');
				res = $('<div />').text(res).html();
				return res.replace(/\*\*\*/g, '\n').replace(/></g, '>\n<');
			},

			get_stack_text : function() {
				var stack_text = "", stack_texts = this.debug_info.split("{[br/]}"), s_idx, stack_lines;
				for (s_idx = 0; s_idx < stack_texts.length; s_idx++) {
					stack_lines = stack_texts[s_idx].split("|");
					if (stack_lines.length === 1) {
						stack_text += stack_lines;
					} else {
						if (stack_lines.length > 1) {
							stack_text += stack_lines[1].rpad(' ', 50);
						}
						if (stack_lines.length > 2) {
							stack_text += stack_lines[2].rpad(' ', 5);
						}
						if (stack_lines.length > 3) {
							stack_text += stack_lines[3];
						}
					}
					stack_text += "\n";
				}
				return stack_text.trim();
			},

			show : function(aTitle, aGUIType) {
				this._super(aTitle, aGUIType);
				this.setActive(true);
				this.except_show();
				this.close(true);
			},

			except_show : function() {
				var jcnt, err_title = '', image_name = '', image_url = '', table = [], acts = [], titles = [], contents = [], extra_id, rep, pos, comp, current_gui, self;
				switch (this.code) {
				case FAILURE:
				case CRITIC:
					image_name = "error";
					err_title = Singleton().getTranslate('Error');
					break;
				case GRAVE:
				case IMPORTANT:
					image_name = "warning";
					err_title = Singleton().getTranslate('Warning');
					break;
				case MINOR:
					image_name = "info";
					err_title = Singleton().getTranslate('Information');
					break;
				default:
					image_name = "error";
					err_title = Singleton().getTranslate('Error');
					break;
				}
				image_url = 'images/' + image_name + '.png';
				table[0] = [];
				table[0][0] = new compBasic("<img src='" + image_url + "' alt='" + image_name + "'></img>");
				table[0][1] = new compBasic("<label style='max-width:800px;overflow:auto;'><b>" + this.message.convertLuctoriosFormatToHtml() + "</b></label>", 1, 1,
						'width:100%;text-align:center;');

				if ((this.code === FAILURE) || (this.code === CRITIC) || (this.code === GRAVE)) {
					if (this.stack_text !== '') {
						titles.push(Singleton().getTranslate("Call-stack"));
						contents.push("<pre>" + this.stack_text + "</pre>");
					}
					extra_id = contents.length;
					titles.push("Extra");
					contents.push("<label>" + this.type + "</label>");
					if (this.requette !== '') {
						titles.push(Singleton().getTranslate("Requette"));
						contents.push("<pre>" + this.get_info(this.requette) + "</pre>");
					}
					if (this.reponse !== '') {
						rep = this.reponse;
						pos = rep.indexOf("?>");
						if (pos >= 0) {
							rep = rep.substring(pos + 2);
						}
						pos = rep.indexOf("<REPONSES");
						if (pos >= 0) {
							if (pos > 0) {
								contents[extra_id] = rep.substring(0, pos - 1).trim();
							}
							titles.push(Singleton().getTranslate("Reponse"));
							contents.push("<pre>" + this.get_info(rep.substring(pos)) + "</pre>");
						} else {
							contents[extra_id] = rep.trim();
						}
					}

					table[1] = [];
					table[1][0] = new compBasic("<input type='button' name='info' value='>>'/><input type='button' name='send' value='"
							+ Singleton().getTranslate("Sent to support") + "'/>", 2, 1, 'text-align:center;');
					table[2] = [];
					table[2][0] = new compBasic(createTab(titles, contents), 2, 1);
				}
				self = this;
				this.mGUI = new GUIManage(this.getId(), err_title, null);

				if (G_Multi_Server === true) {
					acts[0] = new ActionInt();
					acts[0].initializeEx(null, null, Singleton().getTranslate("Servers"));
					acts[0].mIcon = "images/status.png";
					acts[0].callback = config_servers;
					extra_id = 1;
				} else {
					extra_id = 0;
				}
				acts[extra_id] = new ActionInt();
				acts[extra_id].initializeEx(null, null, Singleton().getTranslate("Close"));
				acts[extra_id].mIcon = "images/close.png";
				acts[extra_id].callback = $.proxy(this.mGUI.close, this.mGUI);

				this.mGUI.addcontent(createTable(table), acts);
				this.mGUI.showGUI(true);
				comp = this.mGUI.getHtmlDom();
				current_gui = this.mGUI;
				comp.find("input[name='info']").click(function() {
					if ($(this).attr('value') === ">>") {
						$(this).attr('value', "<<");
						comp.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0)").show();
					} else {
						$(this).attr('value', ">>");
						comp.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0)").hide();
					}
					current_gui.moveCenter();
				});
				this.mGUI.getHtmlDom().find("input[name='send']").click(function() {
					window.location = self.sendSupport();
				});
				comp.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0)").hide();
				this.mGUI.moveCenter();
				jcnt = this.mGUI.getHtmlDom();
				jcnt[0].style.height = (jcnt[0].clientHeight + 10) + 'px';
				jcnt[0].style.width = (jcnt[0].clientWidth + 5) + 'px';
			},

			sendSupport : function() {
				var complement = Singleton().getTranslate("Describ your problem.<br>Thanks<br><br>");
				complement += "<h1>" + this.message + "</h1>";
				if (this.stack_text !== '') {
					complement += this.stack_text + "<br><br>";
				}
				return Singleton().mDesc.fillEmailSupport(Singleton().getTranslate("Bug report"), complement);
			}

		});

var alert_function = function(message) {
	var obs = new ObserverException();
	obs.setContent({
		"exception" : {
			"message" : message,
			"code" : IMPORTANT,
			"debug" : "",
			"type" : "",
			"requette" : "",
			"reponse" : ""
		}
	});
	obs.show('alert');
};

window.onerror = function myErrorHandler(errorMsg, source, lineno, columnNo, error) {
	var error_desc, stack, obs, type_error, errname;
	stack = source + "->" + lineno + ':' + columnNo;
	if (error !== undefined) {
		if (error.type !== undefined) {
			type_error = error.type;
			errname = 'LucteriosException';
			error_desc = [];
			error_desc[0] = error.message;
			error_desc[1] = error.info;
			if (error.extra !== undefined) {
				error_desc[2] = error.extra.toString();
			}
			if (error.fileName !== undefined) {
				stack = error.fileName + ":" + error.lineNumber + ':' + error.columnNumber;
			}
		} else {
			type_error = FAILURE;
			errname = error.name;
			error_desc = [];
			error_desc[0] = error.message;
			error_desc[1] = '*';
			stack = error.stack;
		}
	} else {
		error_desc = [];
		error_desc[0] = errorMsg;
		stack = source + "->" + lineno + ':' + columnNo;
		type_error = FAILURE;
	}
	error_desc[1] = error_desc[1] ? encodeURIComponent(error_desc[1]) : '';
	error_desc[2] = error_desc[2] ? encodeURIComponent(error_desc[2]) : '';
	obs = new ObserverException();
	obs.setContent({
		"exception" : {
			"message" : error_desc[0],
			"code" : type_error,
			"debug" : stack,
			"type" : errname,
			"requette" : error_desc[1],
			"reponse" : error_desc[2]
		}
	});
	/*
	 * + "<TYPE>{0}</TYPE>".format(errname) + "<REQUETTE>{0}</REQUETTE>".format(error_desc[1] ?
	 * encodeURIComponent(error_desc[1]) : '') + "<REPONSE>{0}</REPONSE>".format(error_desc[2] ?
	 * encodeURIComponent(error_desc[2]) : '') + "</EXCEPTION></Error>").parseXML());
	 */
	obs.show('Exception');
	return false;
};
