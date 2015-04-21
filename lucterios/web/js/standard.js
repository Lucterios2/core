/*global $,HashMap,SingletonObj,SingletonClose,Singleton,set_InitialCallBack,GUIManage,compBasic,createTable,createGuid,FAILURE,g_InitialCallBack,G_Version,refreshCurrentAcideMenu,AUTH_PARAM_NAME*/
/*global HttpTransportImpl,ObserverFactoryImpl,ObserverFactoryRestImpl,ActionImpl,ObserverAuthentification,ObserverMenu,ObserverDialogBox,ObserverCustom,ObserverAcknowledge,ObserverException,ObserverPrint*/

function refresh_function() {
	$("#lucteriosClient").html('<div class="waiting"/>');
	var act = Singleton().CreateAction();
	act.initializeEx(null, Singleton().Factory(), '', AUTH_PARAM_NAME[4],
			'authentification');
	act.getParameters = function() {
		var param = new HashMap();
		param.put('info', 'true');
		param.put('ses', Singleton().Transport().getSession());
		return param;
	};
	act.actionPerformed();
}

function standard_initial() {
	$("#lucteriosClient").html('<div class="waiting"/>');

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

	Singleton().Factory().AddObserver("CORE.Auth", ObserverAuthentification);
	Singleton().Factory().AddObserver("CORE.Menu", ObserverMenu);
	Singleton().Factory().AddObserver("Core.DialogBox", ObserverDialogBox);
	Singleton().Factory().AddObserver("Core.Custom", ObserverCustom);
	Singleton().Factory().AddObserver("Core.Acknowledge", ObserverAcknowledge);
	Singleton().Factory().AddObserver("CORE.Exception", ObserverException);
	Singleton().Factory().AddObserver("Core.Print", ObserverPrint);
	// Singleton().Factory().AddObserver("Core.Template", ObserverTemplate);
}

function disconnect_function() {
	standard_initial();
	var obs = new ObserverAuthentification();
	obs.setContent('<NULL/>'.parseXML());
	obs.show_logon('');
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

function aboutmore_function() {
	var table = [];
	table[0] = [];
	table[0][0] = new compBasic(Singleton().mDesc.getHTML(''));
	this.mGUI = new GUIManage(createGuid(), Singleton().getTranslate(
			"Configuration"), null);
	this.mGUI.addcontent(createTable(table), []);
	this.mGUI.showGUI(true);
}

function sendsupport_function() {
	var complement = Singleton().getTranslate(
			"Describ your problem.<br>Thanks<br><br>");
	window.location = Singleton().mDesc.fillEmailSupport(Singleton().getTranslate("Bug report"), complement);
}

function about_function() {
	var mDescription = Singleton().mDesc, table = [];
	table[0] = [];
	table[0][0] = new compBasic("<img src='" + mDescription.getLogoIconName()
			+ "'>", 1, 2);
	table[0][1] = new compBasic("<center><h1>" + mDescription.getTitle()
			+ "</h1></center>", 2, 1);
	table[1] = [];
	table[1][1] = new compBasic("<table width='100%'>" + "<tr><td><center>"
			+ Singleton().getTranslate("Version")
			+ "</center></td><td><center>" + mDescription.getApplisVersion()
			+ "</center></td></tr>"
			+ "<tr><td colspan='2'><font size='-1'><center><i>"
			+ mDescription.getCopyRigth() + "</i></center></font></td><td>"
			+ "</table>", 2, 1);

	table[2] = [];
	table[2][0] = new compBasic(
			"<HR SIZE='2' WIDTH='100%' ALIGN=center>"
					+ "<table width='100%'>"
					+ "<tr><td colspan='2'><font size='+1'><center>" + Singleton().getTranslate("Use the <i>Lucterios</i> framework") + "</center></font></td><td>"
					+ "<tr><td><center>" + Singleton().getTranslate("Server") + "</td><td><center>"
					+ mDescription.getServerVersion() + "</center></td></tr>"
					+ "<tr><td><center>" + Singleton().getTranslate("AJAX client") + "</td><td><center>"
					+ G_Version + "</center></td></tr>" + "</table>", 3);
	table[3] = [];
	table[3][0] = new compBasic(
			"<center><img src='images/LucteriosImage.gif'></center>", 3);
	table[4] = [];
	table[4][0] = new compBasic(
			"<center><font size='-1'><center><i>" + Singleton().getTranslate("Tool of customize management on GPL license") + "</i></center></font></center>",
			3);
	table[5] = [];
	table[5][0] = new compBasic(
			"<center><a href='http://www.lucterios.org'>http://www.lucterios.org</a></center>",
			3);

	table[6] = [];
	table[6][1] = new compBasic(
			"<input type='button' id='send_support' value='" + Singleton().getTranslate("ask support") + "'>",
			1, 1, 'width:100%;');
	table[6][2] = new compBasic(
			"<input type='button' id='aboutmore' value='...'/>", 1);

	this.mGUI = new GUIManage(createGuid(), Singleton().getTranslate("About..."), null);
	this.mGUI.addcontent(createTable(table), []);
	this.mGUI.showGUI(true);
	$("#aboutmore").click(aboutmore_function);
	$("#send_support").click(sendsupport_function);
}

function initial_function() {
	if (Singleton().mDesc === null) {
		Singleton().close();
		first_action();
	} else {
		var disconnect_title = Singleton().getTranslate('Logon'), html, help_url, act;
		if (Singleton().mDesc.getLogin() === '') {
			disconnect_title = Singleton().getTranslate('Logoff');
		}
		help_url = "Help";
		html = "<div id='status' class='ui-widget ui-widget-content ui-corner-all'>"
				+ "<label style='width:280px;margin:5px;'>"
				+ Singleton().mDesc.getConnectUser()
				+ "</label>"
				+ "<label id='disconnect' class='ui-widget-header ui-corner-all' >"
				+ disconnect_title
				+ "</label>"
				+ "<label id='refresh' class='ui-widget-header ui-corner-all' >" + Singleton().getTranslate('Refresh') + "</label>"
				+ "<label id='about' class='ui-widget-header ui-corner-all' >" + Singleton().getTranslate("About...") + "</label>"
				+ "<a href='{0}' target='_blank'><img src='{1}' /></a>".format(
						Singleton().Transport().getIconUrl(help_url),
						Singleton().Transport().getIconUrl('images/help.png'))
				+ "</div>";
		$("#lucteriosClient").append(html);
		$("#refresh").click(refresh_function);
		if (Singleton().mDesc.getMode() === '2') {
			$("#disconnect").css('visibility', 'hidden');
		} else {
			$("#disconnect").click(disconnect_function);
		}
		$("#about").click(about_function);
		document.title = "{0} - {1}".format(Singleton().mDesc.getTitle(),
				Singleton().mDesc.getSubTitle());
		if (Singleton().mRefreshMenu) {
			act = Singleton().CreateAction();
			act.initializeEx(null, Singleton().Factory(), '', 'CORE', 'menu');
			act.actionPerformed();
		}
	}
}

window.onerror = function myErrorHandler(errorMsg, url, lineNumber) {
	var error_desc = errorMsg.split('#'), stack = '', obs, type_error;
	if (lineNumber > 0) {
		stack = url + "->" + lineNumber;
	}
	obs = new ObserverException();
	type_error = FAILURE;
	error_desc[0] = error_desc[0].replace(/uncaught exception: /gi, '');
	if (/[0-9]~/.test(error_desc[0].substr(0, 2))) {
		type_error = error_desc[0].substr(0, 1);
		error_desc[0] = error_desc[0].substr(2);
	}
	obs.setContent(("<Error><EXCEPTION>"
			+ "<MESSAGE>{0}</MESSAGE>".format(error_desc[0])
			+ "<CODE>{0}</CODE>".format(type_error)
			+ "<DEBUG_INFO>|{0}</DEBUG_INFO>".format(stack)
			+ "<TYPE>Ajax exception</TYPE>"
			+ "<REQUETTE>{0}</REQUETTE>"
					.format(error_desc[1] ? encodeURIComponent(error_desc[1])
							: '')
			+ "<REPONSE>{0}</REPONSE>"
					.format(error_desc[2] ? encodeURIComponent(error_desc[2])
							: '') + "</EXCEPTION></Error>").parseXML());
	obs.show('Exception');
	return false;
};

set_InitialCallBack(initial_function);
first_action();
setInterval(refreshCurrentAcideMenu, 5 * 60 * 1000); // Watchdog 5 min
