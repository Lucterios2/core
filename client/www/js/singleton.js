/*global $,Class,HashMap,post_log,g_translation, Uint8Array, unusedVariables, URL, device*/

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
		var offset, blob, sliceSize = 512, byteCharacters = atob(aContent), byteArrays, idx, byteArray, byteNumbers, slice, mouseEvent, hyperlink;
		byteArrays = new [].constructor();
		for (offset = 0; offset < byteCharacters.length; offset += sliceSize) {
			slice = byteCharacters.slice(offset, offset + sliceSize);
			byteNumbers = new [].constructor(slice.length);
			for (idx = 0; idx < slice.length; idx++) {
				byteNumbers[idx] = slice.charCodeAt(idx);
			}
			byteArray = new Uint8Array(byteNumbers);
			byteArrays.push(byteArray);
		}
		blob = new Blob(byteArrays, {
			type : 'application/x-json'
		});
		if (window.navigator.msSaveOrOpenBlob) {
			window.navigator.msSaveOrOpenBlob(blob, aFileName);
		} else {
			hyperlink = document.createElement('a');
			hyperlink.href = URL.createObjectURL(blob);
			hyperlink.target = '_blank';
			hyperlink.download = aFileName;
			mouseEvent = document.createEvent('MouseEvent');
			mouseEvent.initMouseEvent('click', true, true, window, 0, 0, 0, 80, 20, false, false, false, false, 0, null);
			hyperlink.dispatchEvent(mouseEvent);
			if (window.URL) {
				window.URL.revokeObjectURL(hyperlink.href);
			} else if (window.webkitURL) {
				window.webkitURL.revokeObjectURL(hyperlink.href);
			}
		}
	},

	old_saveFile : function(aContent, aFileName) {
		var hyperlink = document.createElement('a'), mouseEvent;
		hyperlink.href = 'data:application/x-json;base64,' + aContent;
		hyperlink.target = '_blank';
		hyperlink.download = aFileName;

		mouseEvent = document.createEvent('MouseEvent');
		mouseEvent.initMouseEvent('click', true, true, window, 0, 0, 0, 80, 20, false, false, false, false, 0, null);
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
		unusedVariables();
	},

	getSelectLang : function() {
		if ((this.mSelectLang === null) && (this.mDesc !== null) && (this.mDesc.getLanguage() !== '')) {
			this.mSelectLang = this.mDesc.getLanguage();
			if ($.datepicker.regional.hasOwnProperty(this.mSelectLang)) {
				$.datepicker.setDefaults($.datepicker.regional[this.mSelectLang]);
			}
		}
		if (this.mSelectLang === null) {
			return "fr";
		}
		return this.mSelectLang;
	},

	getTranslate : function(name) {
		var res = null, select_lang = this.getSelectLang();
		if (g_translation.get(select_lang) !== null) {
			res = g_translation.get(select_lang).get(name);
		}
		if (res === null) {
			res = name;
		}
		return res;
	},

	setHttpTransportClass : function(aTransportClass) {
		this.mTransportObj = null;
		this.mTransportClass = aTransportClass;
	},

	setActionClass : function(aActionClass) {
		this.mActionObj = null;
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

	setInfoDescription : function(aDesc, aRefreshMenu, aInitialHeader) {
		this.mDesc = aDesc;
		this.mSelectLang = null;
		this.mRefreshMenu = aRefreshMenu;
		if (g_InitialCallBack !== null) {
			g_InitialCallBack(aInitialHeader);
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
		SingletonObj = new SingletonClass();
	}
	return SingletonObj;
};

var SingletonClose = function() {
	if (SingletonObj !== null) {
		SingletonObj.close();
	}
	SingletonObj = null;
};

var get_device_info = function() {
	return Singleton().getTranslate("{0} on {1}").format(device.platform, device.model);
};
