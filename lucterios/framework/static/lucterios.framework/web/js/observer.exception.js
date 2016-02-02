/*global $,ObserverAbstract,Singleton, compBasic, GUIManage, createTable, createTab, unusedVariables, FAILURE, CRITIC, GRAVE, IMPORTANT, MINOR*/

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

			setContent : function(aDomXmlContent) {
				this._super(aDomXmlContent);
				var xml_error = this.mDomXmlContent
						.getElementsByTagName("EXCEPTION")[0];
				this.message = xml_error.getCDataOfFirstTag("MESSAGE")
						.convertLuctoriosFormatToHtml();
				this.code = parseInt(
						"0" + xml_error.getCDataOfFirstTag("CODE"), 10);
				this.debug_info = xml_error.getCDataOfFirstTag("DEBUG_INFO")
						.replace(/\{\[br\/\]\}/g, "{[newline]}");
				this.type = xml_error.getCDataOfFirstTag("TYPE");

				this.requette = decodeURIComponent(xml_error
						.getCDataOfFirstTag("REQUETTE").replace('+', ' '));
				if (this.requette === '') {
					this.requette = Singleton().Factory().m_XMLParameters;
				}
				this.reponse = decodeURIComponent(xml_error.getCDataOfFirstTag(
						"REPONSE").replace('+', ' '));
				this.stack_text = this.get_stack_text();
			},

			get_info : function(aInfo) {
				var res = aInfo.replace(/\n/g, '***');
				res = $('<div />').text(res).html();
				return res.replace(/\*\*\*/g, '\n').replace(/></g, '>\n<');
			},

			get_stack_text : function() {
				var stack_text = "", stack_texts = this.debug_info
						.split("{[newline]}"), s_idx, stack_lines;
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
				var err_title = '', image_name = '', image_url = '', table = [], titles = [], contents = [], extra_id, rep, pos, comp, current_gui, self;
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
				image_url = Singleton().Transport().getIconUrl(
						'static/lucterios.CORE/images/' + image_name + '.png');
				table[0] = [];
				table[0][0] = new compBasic("<img src='" + image_url
						+ "' alt='" + image_name + "'></img>");
				table[0][1] = new compBasic(
						"<label style='max-width:800px;overflow:auto;'><b>"
								+ this.message + "</b></label>", 1, 1,
						'width:100%;text-align:center;');

				if ((this.code === FAILURE) || (this.code === CRITIC)
						|| (this.code === GRAVE)) {
					if (this.stack_text !== '') {
						titles.push(Singleton().getTranslate("Call-stack"));
						contents.push("<pre>" + this.stack_text + "</pre>");
					}
					extra_id = contents.length;
					titles.push("Extra");
					contents.push("<label>" + this.type + "</label>");
					if (this.requette !== '') {
						titles.push(Singleton().getTranslate("Requette"));
						contents.push("<pre>" + this.get_info(this.requette)
								+ "</pre>");
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
								contents[extra_id] = rep.substring(0, pos - 1)
										.trim();
							}
							titles.push(Singleton().getTranslate("Reponse"));
							contents.push("<pre>"
									+ this.get_info(rep.substring(pos))
									+ "</pre>");
						} else {
							contents[extra_id] = rep.trim();
						}
					}

					table[1] = [];
					table[1][0] = new compBasic(
							"<input type='button' name='info' value='>>'/><input type='button' name='send' value='"
									+ Singleton().getTranslate(
											"Sent to support") + "'/>", 2, 1,
							'text-align:center;');
					table[2] = [];
					table[2][0] = new compBasic(createTab(titles, contents), 2,
							1);
				}

				self = this;
				this.mGUI = new GUIManage(this.getId(), err_title, null);
				this.mGUI.addcontent(createTable(table), []);
				this.mGUI.showGUI(true);
				comp = this.mGUI.getHtmlDom();
				current_gui = this.mGUI;
				comp
						.find("input[name='info']")
						.click(
								function() {
									if ($(this).attr('value') === ">>") {
										$(this).attr('value', "<<");
										comp
												.find(
														"table:eq(0) > tbody > tr:eq(2) > td:eq(0)")
												.show();
									} else {
										$(this).attr('value', ">>");
										comp
												.find(
														"table:eq(0) > tbody > tr:eq(2) > td:eq(0)")
												.hide();
									}
									current_gui.moveCenter();
								});
				this.mGUI.getHtmlDom().find("input[name='send']").click(
						function() {
							window.location = self.sendSupport();
						});
				comp.find("table:eq(0) > tbody > tr:eq(2) > td:eq(0)").hide();
				this.mGUI.moveCenter();
				this.mGUI.memorize_size();
			},

			sendSupport : function() {
				var complement = Singleton().getTranslate(
						"Describ your problem.<br>Thanks<br><br>");
				complement += "<h1>" + this.message + "</h1>";
				if (this.stack_text !== '') {
					complement += this.stack_text + "<br><br>";
				}
				return Singleton().mDesc.fillEmailSupport(Singleton()
						.getTranslate("Bug report"), complement);
			}

		});
