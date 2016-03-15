/*global $,Class,HashMap,post_log,g_translation*/

var SingletonObj = null;
var g_InitialCallBack = null;
var g_CleanCallBack = null;

function set_InitialCallBack(call_back) {
	g_InitialCallBack = call_back;
}
function set_CleanCallBack(call_back) {
	g_CleanCallBack = call_back;
}
function run_CleanCallBack() {
	if (g_CleanCallBack !== null) {
		g_CleanCallBack();
	}
}

var FileManager = Class.extend({

	saveBlob : function(aBlob, aFileName) {
		var reader = new FileReader();
		reader.onload = $.proxy(function(event) {
			var content = event.target.result, pos;
			if (content.substr(0, 5) === 'data:') {
				pos = content.indexOf(';base64,');
				content = content.substr(pos + 8);
			}
			this.saveFile(content, aFileName);
		}, this);
		reader.readAsDataURL(aBlob);
	},

	saveFile : function(aContent, aFileName) {
		var hyperlink = document.createElement('a'), mouseEvent;
		hyperlink.href = 'data:application/x-json;base64,' + aContent;
		hyperlink.target = '_blank';
		hyperlink.download = aFileName;

		mouseEvent = document.createEvent('MouseEvent');
		mouseEvent.initMouseEvent('click', true, true, window, 0, 0, 0, 80, 20,
				false, false, false, false, 0, null);
		hyperlink.dispatchEvent(mouseEvent);
		if (window.URL) {
			window.URL.revokeObjectURL(hyperlink.href);
		} else if (window.webkitURL) {
			window.webkitURL.revokeObjectURL(hyperlink.href);
		}
	}

});

var SingletonClass = Class.extend({
	mTransportClass : null,
	mActionClass : null,

	mTransportObj : null,
	mFactory : null,
	mDesc : null,
	mRefreshMenu : true,

	mFileManager : new FileManager(),

	mActionList : new HashMap(),

	mSelectLang : null,

	init : function() {
		var languages = navigator.languages, lang_idx, sub_language;
		this.mSelectLang = null;
		if ((languages !== undefined) && (languages !== null)) {
			for (lang_idx = 0; (this.mSelectLang === null)
					&& (lang_idx < languages.length); lang_idx++) {
				sub_language = languages[lang_idx].split('-')[0];
				if (g_translation.hasOwnProperty(languages[lang_idx])) {
					this.mSelectLang = languages[lang_idx];
				} else if (g_translation.hasOwnProperty(sub_language)) {
					this.mSelectLang = sub_language;
				}
			}
		}
		if (this.mSelectLang === null) {
			this.mSelectLang = 'fr';
		}
		post_log("Lang:" + navigator.languages + " - select:"
				+ this.mSelectLang);
		if ($.datepicker.regional.hasOwnProperty(this.mSelectLang)) {
			$.datepicker.setDefaults($.datepicker.regional[this.mSelectLang]);
		}
	},
	
	getSelectLang : function() {
		if ((this.mDesc!==null) && (this.mDesc.getLanguage()!=='')) {
			return this.mDesc.getLanguage();
		}   
		return this.mSelectLang;
	},

	getTranslate : function(name) {
		var res = null, select_lang=this.getSelectLang();
		if (g_translation.get(select_lang) !== null) {
			res = g_translation.get(select_lang).get(name);
		}
		if (res === null) {
			res = name;
		}
		return res;
	},

	setHttpTransportClass : function(aTransportClass) {
		this.mTransportClass = aTransportClass;
	},

	setActionClass : function(aActionClass) {
		this.mActionClass = aActionClass;
	},

	setFactory : function(aFactory) {
		this.mFactory = aFactory;
	},

	Factory : function() {
		return this.mFactory;
	},

	Transport : function() {
		if (this.mTransportObj === null) {
			this.mTransportObj = new this.mTransportClass();
		}
		return this.mTransportObj;
	},

	CreateAction : function() {
		if (this.mActionClass !== null) {
			return new this.mActionClass();
		}
		return null;
	},

	setInfoDescription : function(aDesc, aRefreshMenu) {
		this.mDesc = aDesc;
		this.mRefreshMenu = aRefreshMenu;
		if (g_InitialCallBack !== null) {
			g_InitialCallBack();
		}
	},

	close : function() {
		if (this.mTransportObj !== null) {
			this.mTransportObj.close();
			this.mTransportObj = null;
		}
		this.mDesc = null;
		this.mRefreshMenu = '';
		this.mFactory = null;
	}
});

var Singleton = function() {
	if (SingletonObj === null) {
		post_log("Create Singleton");
		SingletonObj = new SingletonClass();
	}
	return SingletonObj;
};

var SingletonClose = function() {
	if (SingletonObj !== null) {
		SingletonObj.close();
		post_log("Close Singleton");
	}
	SingletonObj = null;
};
