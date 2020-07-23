/*global $,HashMap,SingletonObj,SingletonClose,Singleton,set_InitialCallBack,GUIManage,compBasic,createTable,createGuid,FAILURE,set_CleanCallBack,refreshCurrentAcideMenu,info_openclose,ActionInt*/
/*global HttpTransportImpl,HttpTransportLocal,ObserverFactoryImpl,ObserverFactoryRestImpl,ActionImpl,ObserverAuthentification,ObserverMenu,ObserverDialogBox,ObserverCustom,ObserverAcknowledge,ObserverException,ObserverPrint*/
/*global LucteriosException,IMPORTANT,get_device_info, get_serverurl, G_Multi_Server, ServerManager */

function insertStyle(rule) {
	var css = document.createElement("style");
	css.type = "text/css";
	css.innerHTML = rule;
	document.body.appendChild(css);
}

function clean_function() {
	$("body > div").each(function() {
		var id = $(this).attr('id');
		if (id !== 'lucteriosClient') {
			$(this).remove();
		}
	});
	$("#lucteriosClient").html('<div class="waiting"/>');
}

function refresh_function() {
	clean_function();
	var act = Singleton().CreateAction();
	act.initializeEx(null, Singleton().Factory(), '', 'CORE', 'authentification', 'POST');
	act.getParameters = function() {
		var param = new HashMap();
		param.put('info', 'true');
		param.put('ses', Singleton().Transport().getSession());
		return param;
	};
	act.actionPerformed();
}

function standard_initial() {
	clean_function();

	$(document).on({
		ajaxStart : function() {
			$("body").addClass("loading");
		},
		ajaxStop : function() {
			$("body").removeClass("loading");
		}
	});

	if ((SingletonObj !== null) && (Singleton().mDesc !== null)) {
		document.title = Singleton().mDesc.getTitle();
	} else {
		document.title = "Lucterios";
	}

	SingletonClose();
	Singleton().setHttpTransportClass(HttpTransportImpl);
	Singleton().setFactory(new ObserverFactoryRestImpl());
	Singleton().Factory().setHttpTransport(Singleton().Transport());
	Singleton().setActionClass(ActionImpl);

	Singleton().Factory().clearObserverList();

	Singleton().Factory().AddObserver("core.auth", ObserverAuthentification);
	Singleton().Factory().AddObserver("core.menu", ObserverMenu);
	Singleton().Factory().AddObserver("core.dialogbox", ObserverDialogBox);
	Singleton().Factory().AddObserver("core.custom", ObserverCustom);
	Singleton().Factory().AddObserver("core.acknowledge", ObserverAcknowledge);
	Singleton().Factory().AddObserver("core.exception", ObserverException);
	Singleton().Factory().AddObserver("core.print", ObserverPrint);
}

function disconnect_function() {
	var act = Singleton().CreateAction();
	act.initializeEx(null, Singleton().Factory(), '', 'CORE', 'exitConnection');
	act.actionPerformed();
}

function first_action() {
	standard_initial();
	var session = Singleton().Transport().getSession();
	if (session === "") {
		Singleton().Factory().setAuthentification('', '');
	} else {
		Singleton().Factory().setAuthentification(null, session);
	}
}

function config_servers() {
	/*global main*/
	var servers_mng;
	clean_function();
	Singleton().setHttpTransportClass(HttpTransportLocal);
	Singleton().setFactory(new ObserverFactoryRestImpl());
	Singleton().setActionClass(ActionInt);
	Singleton().Factory().clearObserverList();

	document.title = Singleton().getTranslate("Configuration");
	if (G_Multi_Server === false) {
		throw new LucteriosException(IMPORTANT, "No configuration !");
	}
	servers_mng = new ServerManager();
	servers_mng.reload = main;
	servers_mng.show();
}

function aboutmore_function() {
	var table = [];
	table[0] = [];
	table[0][0] = new compBasic(Singleton().mDesc.getHTML(''));
	this.mGUI = new GUIManage(createGuid(), Singleton().getTranslate("Configuration"), null);
	this.mGUI.addcontent(createTable(table), []);
	this.mGUI.showGUI(true);
}

function help_function() {
	var win = window.open(Singleton().Transport().getIconUrl("Docs"), '_blank');
	win.focus();
}

function sendsupport_function() {
	var complement = Singleton().getTranslate("Describ your problem.<br>Thanks<br><br>");
	window.location = Singleton().mDesc.fillEmailSupport(Singleton().getTranslate("Bug report"), complement);
}

function about_function() {
	var mDescription = Singleton().mDesc, table = [], html, acts = [];
	table[0] = [];
	table[0][0] = new compBasic("<img src='" + mDescription.getLogoIconName() + "'>", 1, 2);
	table[0][1] = new compBasic("<center><h1>" + mDescription.getTitle() + "</h1></center>", 2, 1);
	table[1] = [];
	table[1][1] = new compBasic("<table width='100%'>" + "<tr><td><center>" + Singleton().getTranslate("Version") + "</center></td><td><center>"
			+ mDescription.getApplisVersion() + "</center></td></tr>" + "<tr><td colspan='2'><font size='-1'><center><i>"
			+ mDescription.getCopyRigth() + "</i></center></font></td><td>" + "</table>", 2, 1);

	table[2] = [];
	table[2][0] = new compBasic("<HR SIZE='2' WIDTH='100%' ALIGN=center>" + "<table width='100%'>" + "<tr><td colspan='2'><font size='+1'><center>"
			+ Singleton().getTranslate("Use the <i>Lucterios</i> framework") + "</center></font></td><td>" + "<tr><td><center>"
			+ Singleton().getTranslate("Server") + "</center></td><td><center>" + mDescription.getServerVersion() + "</center></td></tr>"
			+ "<tr><td><center>" + Singleton().getTranslate("Cordova client") + "</center></td><td><center>" + mDescription.getCordovaVersionCurrent() + "</center></td></tr>"
			+ "<tr><td><center>" + Singleton().getTranslate("Device client") + "</center></td><td><center>" + get_device_info()
			+ "</center></td></tr>" + "</table>", 3);
	table[3] = [];
	table[3][0] = new compBasic("<center><img src='images/LucteriosImage.png'></center>", 3);
	table[4] = [];
	table[4][0] = new compBasic("<center><font size='-1'><center><i>" + Singleton().getTranslate("Tool of customize management on GPL license")
			+ "</i></center></font></center>", 3);
	table[5] = [];
	html = "<center>";
	html += "<a target='_blank' href='http://www.lucterios.org' style='margin-right:5px;'>http://www.lucterios.org</a> ";
	html += "<a target='_blank' href='http://www.sd-libre.fr' style='margin-left:5px;'>http://www.sd-libre.fr</a><br/>";
	html += Singleton().getTranslate("Thank you for supporting our work.");
	html += '<form id="formDon" target="_blank" action="https://www.paypal.com/cgi-bin/webscr" method="post">';
	html += '<input name="cmd" value="_s-xclick" type="hidden">';
	html += '<input name="hosted_button_id" value="BDGPMSZGYLWT6" type="hidden">';
	html += '<input style="border: 0;" alt="PayPal" name="submit" src="images/bouton-don-v.png" type="image"></form>';
	html += '</center><hr/>';
	table[5][0] = new compBasic(html, 3);

	table[6] = [];
	table[6][0] = new compBasic(mDescription.mSupportHTML.convertLuctoriosFormatToHtml(), 3);

	this.mGUI = new GUIManage(createGuid(), Singleton().getTranslate("About..."), null);

	acts[0] = new ActionInt();
	acts[0].initializeEx(null, null, Singleton().getTranslate("ask support"));
	acts[0].mIcon = "images/right.png";
	acts[0].callback = sendsupport_function;
	acts[1] = new ActionInt();
	acts[1].initializeEx(null, null, Singleton().getTranslate("More..."));
	acts[1].mIcon = "images/info.png";
	acts[1].callback = aboutmore_function;
	acts[2] = new ActionInt();
	acts[2].initializeEx(null, null, Singleton().getTranslate("Close"));
	acts[2].mIcon = "images/close.png";
	acts[2].callback = $.proxy(this.mGUI.close, this.mGUI);

	this.mGUI.addcontent(createTable(table), acts);
	this.mGUI.showGUI(true);
}

function initial_function(aInitialHeader) {
	if (Singleton().mDesc === null) {
		Singleton().close();
		first_action();
	} else {
		var disconnect_title, html, act;
		if (aInitialHeader) {
			$("div#message_before").remove();
			disconnect_title = Singleton().getTranslate('Logoff');
			if (Singleton().mDesc.getLogin() === '') {
				disconnect_title = Singleton().getTranslate('Logon');
			}
			html = "<div id='status'>";
			html += "<div class='header-left'>";
			html += "<label id='showmenu' class='ui-widget-header ui-corner-all'>";
			html += "<span class='fa fa-list-alt'/>" + "<span name='headertle'>";
			html += Singleton().getTranslate('Info');
			html += "</span>";
			html += "</label>";
			html += "<img src='{0}' style='height:48px'>".format(Singleton().mDesc.getLogoIconName());
			html += "<label id='statususer'>";
			html += Singleton().mDesc.getConnectUser();
			html += "</label>";
			html += "</div>";
			html += "<div class='header-right'>";
			html += "<label id='disconnect' class='ui-widget-header ui-corner-all' >";
			html += "<span class='fa fa-power-off'/>" + "<span name='headertle'>";
			html += disconnect_title;
			html += "</span>";
			html += "</label>";
			html += "<label id='refresh' class='ui-widget-header ui-corner-all' >";
			html += "<span class='fa fa-refresh'/>";
			html += "<span name='headertle'>";
			html += Singleton().getTranslate('Refresh');
			html += "</span>";
			html += "</label>";
			if (G_Multi_Server === true) {
				html += "<label id='servers' class='ui-widget-header ui-corner-all' >";
				html += "<span class='fa fa-database'/>";
				html += "<span name='headertle'>";
				html += Singleton().getTranslate('Servers');
				html += "</span>";
				html += "</label>";
			}
			html += "<label id='about' class='ui-widget-header ui-corner-all' >";
			html += "<span class='fa fa-info-circle'/>";
			html += "<span name='headertle'>";
			html += Singleton().getTranslate("About...");
			html += "</span>";
			html += "</label>";
			html += "<label id='help' class='ui-widget-header ui-corner-all' >";
			html += "<span class='fa fa-question-circle'/>";
			html += "<span name='headertle'>";
			html += Singleton().getTranslate("Help");
			html += "</span>";
			html += "</label>";
			html += "</div>";
			html += "</div>";
			$("#lucteriosClient").append(html);
			$("#refresh").click(refresh_function);
			if (Singleton().mDesc.getMode() === '2') {
				$("#disconnect").css('visibility', 'hidden');
			} else {
				$("#disconnect").click(disconnect_function);
			}
			if (G_Multi_Server === true) {
				$("#servers").click(config_servers);
			}
			$("#about").click(about_function);
			$("#help").click(help_function);
			$("#showmenu").click(info_openclose);
			if (Singleton().mRefreshMenu) {
				act = Singleton().CreateAction();
				act.initializeEx(null, Singleton().Factory(), '', 'CORE', 'menu');
				act.actionPerformed();
			}
		} else {
			if (Singleton().mDesc.mMessageBefore !== '') {
				html = "<div id='message_before'>";
				html += Singleton().mDesc.mMessageBefore.convertLuctoriosFormatToHtml();
				html += "</div>";
				$("#lucteriosClient").append(html);
			}
		}
		document.title = "{0} - {1}".format(Singleton().mDesc.getTitle(), Singleton().mDesc.getSubTitle());
		if (Singleton().mDesc.mBackground !== '') {
			$('body').css('background', '#EEE url(' + Singleton().mDesc.mBackground + ') repeat');
		} else {
			$('body').css('background', '');
		}
		$('style[type="text/css"]').remove();
		if (Singleton().mDesc.mStyle !== '') {
			insertStyle(Singleton().mDesc.mStyle);
		}
	}
}

function main() {
	set_InitialCallBack(initial_function);
	set_CleanCallBack(clean_function);
	setInterval(refreshCurrentAcideMenu, 5 * 60 * 1000); // Watchdog 5 min
	if (get_serverurl() !== null) {
		first_action();
	} else {
		config_servers();
	}
}

main();
