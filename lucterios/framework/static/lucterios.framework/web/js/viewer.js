/*global $,HashMap,SingletonObj,SingletonClose,Singleton,set_InitialCallBack,GUIManage,compBasic,createTable,createGuid,FAILURE,set_CleanCallBack,G_Version,refreshCurrentAcideMenu*/
/*global HttpTransportImpl,ObserverFactoryImpl,ObserverFactoryRestImpl,ActionImpl,WrongObserverAuthentification,ObserverMenu,ObserverDialogBox,ObserverCustom,ObserverAcknowledge,ObserverException,ObserverPrint*/

var G_params = {};
try {
	window.location.href.replace(location.hash, '').replace(/[?&]+([^=&]+)=?([^&]*)?/gi, // regexp
	function(m, key, value) { // callback
		G_params[key] = (value !== undefined) ? value : '';
	});
	G_params = atob(G_params['CODE']);
	G_params = jQuery.parseJSON(G_params);
} catch ($exept) {
	G_params = null;
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

	Singleton().Factory().AddObserver("core.auth", WrongObserverAuthentification);
	Singleton().Factory().AddObserver("core.dialogbox", ObserverDialogBox);
	Singleton().Factory().AddObserver("core.custom", ObserverCustom);
	Singleton().Factory().AddObserver("core.acknowledge", ObserverAcknowledge);
	Singleton().Factory().AddObserver("core.exception", ObserverException);
	Singleton().Factory().AddObserver("core.print", ObserverPrint);
}

function first_action() {
	var session;
	standard_initial();
	if ((G_params !== null) && (G_params['ses'] !== undefined)) {
		Singleton().Transport().setSession("");
		Singleton().Transport().setSession(G_params['ses']);
		$.cookie('sessionid', session, {
			path : '/',
			expires : 0.007
		});
	}
	session = Singleton().Transport().getSession();
	if (session === "") {
		Singleton().Factory().setAuthentification('', '');
	} else {
		Singleton().Factory().setAuthentification(null, session);
	}
}

function initial_function() {
	if (Singleton().mDesc === null) {
		Singleton().close();
		first_action();
	} else {
		var html, act;
		if (Singleton().mDesc.getLogin() === '') {
			disconnect_title = Singleton().getTranslate('Logon');
		}
		document.title = "{0} - {1}".format(Singleton().mDesc.getTitle(), Singleton().mDesc.getSubTitle());
		if (G_params !== null) {
			if (G_params['bcg'] === undefined) {
				$('body').css('background', '#EEE url(' + Singleton().mDesc.mBackground + ') repeat');
			} else {
				$('body').css('background', G_params['bcg']);
			}
			act = Singleton().CreateAction();
			act.mFormType = FORM_MODAL;
			act.initializeEx(null, Singleton().Factory(), '', G_params['ext'], G_params['act']);
			act.getParameters = function() {
				var param = new HashMap();
				jQuery.each(G_params['params'], function(key, data) {
					param.put(key, data);
				});
				return param;
			};
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
	error_desc[0] = error_desc[0].replace(/Uncaught /gi, '');
	if (/[0-9]~/.test(error_desc[0].substr(0, 2))) {
		type_error = error_desc[0].substr(0, 1);
		error_desc[0] = error_desc[0].substr(2);
	}
	obs.setContent(("<Error><EXCEPTION>" + "<MESSAGE><![CDATA[{0}]]></MESSAGE>".format(error_desc[0]) + "<CODE>{0}</CODE>".format(type_error)
			+ "<DEBUG_INFO>|{0}</DEBUG_INFO>".format(stack) + "<TYPE>Ajax exception</TYPE>"
			+ "<REQUETTE>{0}</REQUETTE>".format(error_desc[1] ? encodeURIComponent(error_desc[1]) : '')
			+ "<REPONSE>{0}</REPONSE>".format(error_desc[2] ? encodeURIComponent(error_desc[2]) : '') + "</EXCEPTION></Error>").parseXML());
	obs.show('Exception');
	return false;
};

set_InitialCallBack(initial_function);
set_CleanCallBack(clean_function);
first_action();
