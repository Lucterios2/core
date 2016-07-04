/*global $,HashMap,singletonObj,singletonClose,singleton,set_InitialCallBack,GUIManage,CompBasic,createTable,createGuid,FAILURE,set_CleanCallBack,G_Version,refreshCurrentAcideMenu, HTML_HEADER_TEMPLATE*/
/*global HttpTransportImpl,ObserverFactoryImpl,ObserverFactoryRestImpl,ActionImpl,ObserverAuthentification,ObserverMenu,ObserverDialogBox,ObserverCustom,ObserverAcknowledge,ObserverException,ObserverPrint*/


function clean_function() {
	$("body > div").each(function () {
		var id = $(this).attr('id');
		if (id !== 'lucteriosClient') {
			$(this).remove();
		}
	});
	$("#lucteriosClient").html('<div class="waiting"/>');
}

function refresh_function() {
	clean_function();
	var act = singleton().CreateAction();
	act.initializeEx(null, singleton().Factory(), '', 'CORE',
			'authentification');
	act.getParameters = function () {
		var param = new HashMap();
		param.put('info', 'true');
		param.put('ses', singleton().Transport().getSession());
		return param;
	};
	act.actionPerformed();
}

function standard_initial() {
	clean_function();

	$(document).on({
		ajaxStart : function () {
			$("body").addClass("loading");
		},
		ajaxStop : function () {
			$("body").removeClass("loading");
		}
	});

	if ((singletonObj !== null) && (singleton().mDesc !== null)) {
		document.title = singleton().mDesc.getTitle();
	} else {
		document.title = "Lucterios";
	}

	singletonClose();
	singleton().setHttpTransportClass(HttpTransportImpl);
	singleton().setFactory(new ObserverFactoryRestImpl());
	singleton().Factory().setHttpTransport(singleton().Transport());
	singleton().setActionClass(ActionImpl);

	singleton().Factory().clearObserverList();

	singleton().Factory().AddObserver("core.auth", ObserverAuthentification);
	singleton().Factory().AddObserver("core.menu", ObserverMenu);
	singleton().Factory().AddObserver("core.dialogbox", ObserverDialogBox);
	singleton().Factory().AddObserver("core.custom", ObserverCustom);
	singleton().Factory().AddObserver("core.acknowledge", ObserverAcknowledge);
	singleton().Factory().AddObserver("core.exception", ObserverException);
	singleton().Factory().AddObserver("core.print", ObserverPrint);
}

function disconnect_function() {
	standard_initial();
	var obs = new ObserverAuthentification();
	obs.setContent('<NULL/>'.parseXML());
	obs.show_logon('');
}

function first_action() {
	standard_initial();
	var session = singleton().Transport().getSession();
	if (session === "") {
		singleton().Factory().setAuthentification('', '');
	} else {
		singleton().Factory().setAuthentification(null, session);
	}
}

function aboutmore_function() {
	var table = [], mGUI;
	table[0] = [];
	table[0][0] = new CompBasic(singleton().mDesc.getHTML(''));
	mGUI = new GUIManage(createGuid(), singleton().getTranslate("Configuration"), null);
	mGUI.addcontent(createTable(table), []);
	mGUI.showGUI(true);
}

function sendsupport_function() {
	var complement = singleton().getTranslate("Describ your problem.<br>Thanks<br><br>");
	window.location = singleton().mDesc.fillEmailSupport(singleton()
			.getTranslate("Bug report"), complement);
}

function about_function() {
	var mDescription = singleton().mDesc, table = [], mGUI;
	table[0] = [];
	table[0][0] = new CompBasic("<img src='" + mDescription.getLogoIconName()
			+ "'>", 1, 2);
	table[0][1] = new CompBasic("<center><h1>" + mDescription.getTitle()
			+ "</h1></center>", 2, 1);
	table[1] = [];
	table[1][1] = new CompBasic("<table width='100%'>" + "<tr><td><center>"
			+ singleton().getTranslate("Version")
			+ "</center></td><td><center>" + mDescription.getApplisVersion()
			+ "</center></td></tr>"
			+ "<tr><td colspan='2'><font size='-1'><center><i>"
			+ mDescription.getCopyRigth() + "</i></center></font></td><td>"
			+ "</table>", 2, 1);

	table[2] = [];
	table[2][0] = new CompBasic("<HR SIZE='2' WIDTH='100%' ALIGN=center>"
			+ "<table width='100%'>"
			+ "<tr><td colspan='2'><font size='+1'><center>"
			+ singleton().getTranslate("Use the <i>Lucterios</i> framework")
			+ "</center></font></td><td>" + "<tr><td><center>"
			+ singleton().getTranslate("Server") + "</td><td><center>"
			+ mDescription.getServerVersion() + "</center></td></tr>"
			+ "<tr><td><center>" + singleton().getTranslate("AJAX client")
			+ "</td><td><center>" + G_Version + "</center></td></tr>"
			+ "</table>", 3);
	table[3] = [];
	table[3][0] = new CompBasic("<center><img src='images/LucteriosImage.png'></center>", 3);
	table[4] = [];
	table[4][0] = new CompBasic("<center><font size='-1'><center><i>"
			+ singleton().getTranslate("Tool of customize management on GPL license")
			+ "</i></center></font></center>", 3);
	table[5] = [];
	table[5][0] = new CompBasic("<center><a href='http://www.lucterios.org'>http://www.lucterios.org</a></center>", 3);

	table[6] = [];
	table[6][1] = new CompBasic(
        "<input type='button' id='send_support' value='"
            + singleton().getTranslate("ask support") + "'>",
        1,
        1,
        'width:100%;'
    );
	table[6][2] = new CompBasic("<input type='button' id='aboutmore' value='...'/>", 1);

	mGUI = new GUIManage(createGuid(), singleton()
        .getTranslate("About..."), null);
	mGUI.addcontent(createTable(table), []);
	mGUI.showGUI(true);
	$("#aboutmore").click(aboutmore_function);
	$("#send_support").click(sendsupport_function);
}

function initial_function() {
	if (singleton().mDesc === null) {
		singleton().close();
		first_action();
	} else {
		var disconnect_title = singleton().getTranslate('Logoff'), html, act;
		if (singleton().mDesc.getLogin() === '') {
			disconnect_title = singleton().getTranslate('Logon');
		}
		html = HTML_HEADER_TEMPLATE.format(
		    singleton().mDesc.getLogoIconName(),
		    singleton().mDesc.getTitle(),
		    singleton().mDesc.getConnectUser(),
		    singleton().getTranslate('Refresh'),
		    singleton().getTranslate("About..."),
		    singleton().getTranslate("Help"),
		    disconnect_title
		);

        $("nav").remove();
		$("body").append(html);
		$("#BT_refresh").click(refresh_function);
		if (singleton().mDesc.getMode() === '2') {
			$("#BT_logoff").css('visibility', 'hidden');
		} else {
			$("#BT_logoff").click(disconnect_function);
		}
		$("#BT_about").click(about_function);
		$("#BT_help").click(function () {
		    window.open(singleton().Transport().getIconUrl("Docs"));
		});
		document.title = "{0} - {1}".format(singleton().mDesc.getTitle(),
				singleton().mDesc.getSubTitle());
		if (singleton().mRefreshMenu) {
			act = singleton().CreateAction();
			act.initializeEx(null, singleton().Factory(), '', 'CORE', 'menu');
			act.actionPerformed();
		}
		$('body').css('background',
				'#EEE url(' + singleton().mDesc.mBackground + ') repeat');
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

// Init du client au DOM Ready
$(function () {
    // mise en place du loading sur les attentes
    $(document).on({
		ajaxStart : function () {
			$("body").addClass("loading");
		},
		ajaxStop : function () {
			$("body").removeClass("loading");
		}
	});

    // init de la lib de singletons
    set_InitialCallBack(initial_function);
    set_CleanCallBack(clean_function);

	singletonClose();
	singleton().setHttpTransportClass(HttpTransportImpl);
	singleton().setFactory(new ObserverFactoryRestImpl());
	singleton().Factory().setHttpTransport(singleton().Transport());
	singleton().setActionClass(ActionImpl);

	singleton().Factory().clearObserverList();

	singleton().Factory().AddObserver("core.auth", ObserverAuthentification);
	singleton().Factory().AddObserver("core.menu", ObserverMenu);
	singleton().Factory().AddObserver("core.dialogbox", ObserverDialogBox);
	singleton().Factory().AddObserver("core.custom", ObserverCustom);
	singleton().Factory().AddObserver("core.acknowledge", ObserverAcknowledge);
	singleton().Factory().AddObserver("core.exception", ObserverException);
	singleton().Factory().AddObserver("core.print", ObserverPrint);

    // récup du titre de l'application
	if ((singletonObj !== null) && (singleton().mDesc !== null)) {
		document.title = singleton().mDesc.getTitle();
	} else {
		document.title = "Lucterios";
	}

    // init de la session
	var session = singleton().Transport().getSession();
	if (session === "") {
		singleton().Factory().setAuthentification('', '');
	} else {
		singleton().Factory().setAuthentification(null, session);
	}

    // rafraichissement du menu toutes les 5 minutes
    setInterval(refreshCurrentAcideMenu, 5 * 60 * 1000); // Watchdog 5 min
});
