/*global $,HashMap,SingletonObj,SingletonClose,Singleton,set_InitialCallBack,GUIManage,compBasic,createTable,createGuid,FAILURE,set_CleanCallBack,refreshCurrentAcideMenu,unusedVariables,atob,FORM_MODAL*/
/*global HttpTransportImpl,ObserverFactoryImpl,ObserverFactoryRestImpl,ActionImpl,WrongObserverAuthentification,EmptyObserverMenu,ObserverDialogBox,ObserverCustom,ObserverAcknowledge,ObserverException,ObserverPrint*/

var G_params = {};
try {
	/*jslint regexp: true*/
	window.location.href.replace(location.hash, '').replace(/[?&]+([^=&]+)=?([^&]*)?/gi, // regexp
	function(m, key, value) {
		unusedVariables(m);
		G_params[key] = (value !== undefined) ? value : '';
	});
	/*jslint regexp: false*/
	G_params = atob(G_params.CODE);
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
	Singleton().Factory().AddObserver("core.menu", EmptyObserverMenu);
	Singleton().Factory().AddObserver("core.dialogbox", ObserverDialogBox);
	Singleton().Factory().AddObserver("core.custom", ObserverCustom);
	Singleton().Factory().AddObserver("core.acknowledge", ObserverAcknowledge);
	Singleton().Factory().AddObserver("core.exception", ObserverException);
	Singleton().Factory().AddObserver("core.print", ObserverPrint);
}

function first_action() {
	var session;
	standard_initial();
	if ((G_params !== null) && (G_params.ses !== undefined)) {
		Singleton().Transport().setSession("");
		Singleton().Transport().setSession(G_params.ses);
		$.cookie('sessionid', G_params.ses, {
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
		var act;
		document.title = "{0} - {1}".format(Singleton().mDesc.getTitle(), Singleton().mDesc.getSubTitle());
		if (G_params !== null) {
			if (G_params.bcg === undefined) {
				$('body').css('background', '#EEE url(' + Singleton().mDesc.mBackground + ') repeat');
			} else {
				$('body').css('background', G_params.bcg);
			}
			act = Singleton().CreateAction();
			act.mFormType = FORM_MODAL;
			act.initializeEx(null, Singleton().Factory(), '', G_params.ext, G_params.act, G_params.method);
			act.getParameters = function() {
				var param = new HashMap();
				jQuery.each(G_params.params, function(key, data) {
					param.put(key, data);
				});
				return param;
			};
			act.actionPerformed();
		}
	}
}

function main() {
	set_InitialCallBack(initial_function);
	set_CleanCallBack(clean_function);
	first_action();
}

main();
