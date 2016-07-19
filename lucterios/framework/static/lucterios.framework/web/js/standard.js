/*global $,HashMap,SingletonObj,SingletonClose,Singleton,set_InitialCallBack,GUIManage,compBasic,createTable,createGuid,FAILURE,set_CleanCallBack,G_Version,refreshCurrentAcideMenu*/
/*global HttpTransportImpl,ObserverFactoryImpl,ObserverFactoryRestImpl,ActionImpl,ObserverAuthentification,ObserverMenu,ObserverDialogBox,ObserverCustom,ObserverAcknowledge,ObserverException,ObserverPrint*/

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
	act.initializeEx(null, Singleton().Factory(), '', 'CORE',
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

function info_function() {
	var val_display=$("#asideMenu").css('display');
	if (val_display==='none') {
		$("#asideMenu").css('display','block');
	} else {
		$("#asideMenu").css('display','none');
	}
}

function help_function() {
	  var win = window.open(Singleton().Transport().getIconUrl("Docs"), '_blank');
	  win.focus();
}

function sendsupport_function() {
	var complement = Singleton().getTranslate(
			"Describ your problem.<br>Thanks<br><br>");
	window.location = Singleton().mDesc.fillEmailSupport(Singleton()
			.getTranslate("Bug report"), complement);
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
	table[2][0] = new compBasic("<HR SIZE='2' WIDTH='100%' ALIGN=center>"
			+ "<table width='100%'>"
			+ "<tr><td colspan='2'><font size='+1'><center>"
			+ Singleton().getTranslate("Use the <i>Lucterios</i> framework")
			+ "</center></font></td><td>" + "<tr><td><center>"
			+ Singleton().getTranslate("Server") + "</td><td><center>"
			+ mDescription.getServerVersion() + "</center></td></tr>"
			+ "<tr><td><center>" + Singleton().getTranslate("AJAX client")
			+ "</td><td><center>" + G_Version + "</center></td></tr>"
			+ "</table>", 3);
	table[3] = [];
	table[3][0] = new compBasic(
			"<center><img src='images/LucteriosImage.png'></center>", 3);
	table[4] = [];
	table[4][0] = new compBasic("<center><font size='-1'><center><i>"
			+ Singleton().getTranslate(
					"Tool of customize management on GPL license")
			+ "</i></center></font></center>", 3);
	table[5] = [];
	table[5][0] = new compBasic(
			"<center><a href='http://www.lucterios.org'>http://www.lucterios.org</a></center><hr/>",
			3);

	table[6] = [];
	table[6][0] = new compBasic(mDescription.mSupportHTML
			.convertLuctoriosFormatToHtml(), 3);

	table[7] = [];
	table[7][1] = new compBasic(
			"<input type='button' id='send_support' value='"
					+ Singleton().getTranslate("ask support") + "'>", 1, 1,
			'width:100%;');
	table[7][2] = new compBasic(
			"<input type='button' id='aboutmore' value='...'/>", 1);

	this.mGUI = new GUIManage(createGuid(), Singleton()
			.getTranslate("About..."), null);
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
		var disconnect_title = Singleton().getTranslate('Logoff'), html, act;
		if (Singleton().mDesc.getLogin() === '') {
			disconnect_title = Singleton().getTranslate('Logon');
		}
		html = "<div id='status'>"
				+ "<div class='header-left'>"
				+ "<label id='showmenu' class='ui-widget-header ui-corner-all'>"
				+ "<span class='fa fa-menu'/>"
				+ Singleton().getTranslate('Info')
				+ "</label>"
				+ "<img src='{0}' style='height:48px'>"
						.format(Singleton().mDesc.getLogoIconName())
				+ "<label id='statususer'>"
				+ Singleton().mDesc.getConnectUser()
				+ "</label>"
				+ "</div>"
				+ "<div class='header-right'>"
				+ "<label id='disconnect' class='ui-widget-header ui-corner-all' >"
				+ "<span class='fa fa-logon'/>"
				+ "<span name='headertle'>"
				+ disconnect_title
				+ "</span>"
				+ "</label>"
				+ "<label id='refresh' class='ui-widget-header ui-corner-all' >"
				+ "<span class='fa fa-refresh'/>"
				+ "<span name='headertle'>"
				+ Singleton().getTranslate('Refresh')
				+ "</span>"
				+ "</label>"
				+ "<label id='about' class='ui-widget-header ui-corner-all' >"
				+ "<span class='fa fa-about'/>"
				+ "<span name='headertle'>"
				+ Singleton().getTranslate("About...")
				+ "</span>"
				+ "</label>"
				+ "<label id='help' class='ui-widget-header ui-corner-all' >"
				+ "<span class='fa fa-help'/>"
				+ "<span name='headertle'>"
				+ Singleton().getTranslate("Help")
				+ "</span>"
				+ "</label>"
				+ "</div>"
				+ "</div>";
		$("#lucteriosClient").append(html);
		$("#refresh").click(refresh_function);
		if (Singleton().mDesc.getMode() === '2') {
			$("#disconnect").css('visibility', 'hidden');
		} else {
			$("#disconnect").click(disconnect_function);
		}
		$("#about").click(about_function);
		$("#help").click(help_function);
		$("#showmenu").click(info_function);
		document.title = "{0} - {1}".format(Singleton().mDesc.getTitle(),
				Singleton().mDesc.getSubTitle());
		if (Singleton().mRefreshMenu) {
			act = Singleton().CreateAction();
			act.initializeEx(null, Singleton().Factory(), '', 'CORE', 'menu');
			act.actionPerformed();
		}
		$('body').css('background',
				'#EEE url(' + Singleton().mDesc.mBackground + ') repeat');
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
			+ "<MESSAGE><![CDATA[{0}]]></MESSAGE>".format(error_desc[0])
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
set_CleanCallBack(clean_function);
first_action();
setInterval(refreshCurrentAcideMenu, 5 * 60 * 1000); // Watchdog 5 min
